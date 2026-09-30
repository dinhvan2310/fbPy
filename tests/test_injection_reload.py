"""Run with python -m unittest discover -s tests -v (requires Chrome)."""

import tempfile
import unittest

from playwright.sync_api import sync_playwright

from playwright_inject import _build_inject_script, _inject_ready_pages


TARGET = (
    "https://adsmanager.facebook.com/adsmanager/manage/campaigns"
    "?date=2026-09-01_2026-09-30"
)
MARKER = "Boolean(window.__fb_session_injection_v3__)"
TABLE = """
<div class="_3h1i _1mie"><div class="_3h1j">
  <div class="_1eyh _1eyi" style="left:100px">Results </div>
  <div class="_4lg0 _4lg5 _4h2p _4h2m" style="left:100px"><span>1</span></div>
  <div id="total" class="_4lg0 _4lg5 _4h2p _4h2m" style="left:100px"><span>2</span></div>
</div></div>
"""
HTML = f"""<!doctype html><body><script>
// Simulate the app rendering its table after DOMContentLoaded.
setTimeout(() => document.body.insertAdjacentHTML('beforeend', {TABLE!r}), 150);
</script></body>"""


class InjectionReloadTests(unittest.TestCase):
    def setUp(self):
        self.profile = tempfile.TemporaryDirectory(prefix="fbpy-reload-test-")
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            self.profile.name, channel="chrome", headless=True,
        )
        self.context.route("**/*", lambda route: route.fulfill(
            status=200, content_type="text/html", body=HTML,
        ))
        self.context.add_init_script("""(() => {
            window.intervalCount = 0;
            const original = window.setInterval;
            window.setInterval = (...args) => {
                window.intervalCount++;
                return original(...args);
            };
        })()""")
        self.page = self.context.pages[0]
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        rows = [dict(results=n, spent=100, reach=20, views=30) for n in (7, 11)]
        self.script = _build_inject_script({
            "datePresets": {"20260901-20260930": {"campaigns": rows}},
        })

    def tearDown(self):
        self.context.close()
        self.playwright.stop()
        self.profile.cleanup()

    def scan(self):
        _inject_ready_pages(self.context, self.script)

    def assert_effective(self, page=None):
        page = page or self.page
        page.wait_for_function("document.querySelector('#total')?.textContent === '11'")
        self.assertTrue(page.evaluate(MARKER))
        self.assertEqual(self.errors, [])

    def test_same_url_reload_reinjects_and_restores_effect(self):
        self.page.goto(TARGET)
        self.scan()
        self.assert_effective()
        for _ in range(3):
            self.page.reload(wait_until="domcontentloaded")
            self.assertEqual(self.page.url, TARGET)
            self.assertFalse(self.page.evaluate(MARKER))
            self.scan()
            self.assert_effective()

    def test_repeated_scans_and_spa_navigation_do_not_duplicate_timers(self):
        self.page.goto(TARGET)
        self.scan()
        self.assert_effective()
        count = self.page.evaluate("window.intervalCount")
        for _ in range(5):
            self.scan()
        self.page.evaluate("history.replaceState(null, '', location.href + '&act=123')")
        self.scan()
        self.assert_effective()
        self.assertEqual(self.page.evaluate("window.intervalCount"), count)

    def test_return_to_target_and_reopened_tab_inject(self):
        self.page.goto(TARGET)
        self.scan()
        self.assert_effective()
        self.page.goto("https://example.com/")
        self.scan()
        self.assertFalse(self.page.evaluate(MARKER))
        self.page.goto(TARGET)
        self.scan()
        self.assert_effective()
        second = self.context.new_page()
        second.goto(TARGET)
        self.page.close()
        self.scan()
        self.assert_effective(second)

    def test_guard_skips_loading_and_wrong_host_documents(self):
        # At document start the guard must leave the marker unset, so a later
        # scanner can retry when this document becomes ready.
        self.context.add_init_script(self.script)
        self.page.goto(TARGET)
        self.assertFalse(self.page.evaluate(MARKER))
        self.scan()
        self.assert_effective()
        self.page.goto("https://example.com/")
        self.page.evaluate(self.script)
        self.assertFalse(self.page.evaluate(MARKER))


if __name__ == "__main__":
    unittest.main()
