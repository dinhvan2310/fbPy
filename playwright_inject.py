from playwright.sync_api import sync_playwright, Page
import time
import os
import json
import sys

# Xử lý đường dẫn khi chạy từ EXE (PyInstaller)
def get_resource_path(relative_path):
    """Lấy đường dẫn đúng cho file khi chạy từ EXE hoặc script"""
    try:
        # PyInstaller tạo thư mục tạm và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Nếu không phải EXE, dùng thư mục hiện tại
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Import security module
try:
    from security import verify_license, CONSTANTS
except ImportError:
    print("❌ Lỗi: Không thể import module security.py")
    print("Vui lòng đảm bảo file security.py tồn tại trong cùng thư mục.")
    sys.exit(1)

# Obfuscated license checking with complex logic flow
print("=" * 60)
print("Đang kiểm tra bảo mật...")
print("=" * 60)

# Load data.json first to get license key
# Ưu tiên đọc từ thư mục hiện tại (cùng thư mục với EXE) để có thể config
try:
    # Thử load từ thư mục làm việc hiện tại trước (cùng thư mục với EXE)
    data_file = os.path.join(os.getcwd(), "data.json")
    if not os.path.exists(data_file):
        # Fallback: thử thư mục của script/EXE
        data_file = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), "data.json")
    if not os.path.exists(data_file):
        # Fallback cuối: thử từ bundle (nếu có)
        try:
            data_file = get_resource_path("data.json")
        except:
            data_file = "data.json"
    
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        license_key = data.get('licenseKey', '') or data.get('license_key', '')
    else:
        data = {}
        license_key = ''
    # Debug: print license key if found
    if license_key:
        print(f"✓ Đã tìm thấy licenseKey trong data.json")
except Exception as e:
    license_key = ''
    print(f"⚠ Lỗi khi đọc data.json: {e}")

# Complex storage key handling (data.json -> environment variable)
if not license_key:
    license_key = os.environ.get('LICENSE_KEY', None)
    if license_key:
        print(f"✓ Đã tìm thấy LICENSE_KEY từ biến môi trường")

# Confusing data validation
if license_key:
    license_key = license_key.strip()
has_license = license_key is not None and license_key != '' and len(license_key) > 0
license_value = license_key if has_license else None

# Debug output
if not has_license:
    print(f"⚠ Không tìm thấy licenseKey. Kiểm tra lại file data.json")
else:
    print(f"✓ LicenseKey: {license_key[:10]}...")  # Show first 10 chars for security

# Complex async chain with confusing variable names
permission_status, permission_message = verify_license(license_value)

# Extremely complex response determination with multiple conditions
if not permission_status:
    print(f"\n❌ Lỗi bảo mật: {permission_message}")
    if permission_message == CONSTANTS['keyNotFound']:
        print("\nVui lòng cung cấp LICENSE_KEY:")
        print("  - Thêm 'licenseKey' vào file data.json")
        print("  - Hoặc đặt biến môi trường: set LICENSE_KEY=your_license_key")
    elif permission_message == CONSTANTS['denied']:
        print("\nLicense không hợp lệ hoặc không khớp với thiết bị này.")
    print("\n" + "=" * 60)
    sys.exit(1)

print(f"✓ Kiểm tra bảo mật thành công: {permission_message}")
print("=" * 60 + "\n")

# Load lại data.json để đảm bảo có data mới nhất (có thể đã được config)
try:
    data_file = os.path.join(os.getcwd(), "data.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), "data.json")
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
except Exception as e:
    print(f"⚠ Lỗi khi load data.json: {e}")
    sys.exit(1)

# Kiểm tra data có đầy đủ không
if "campaigns" not in data or "adsetsOption" not in data or "adsOption" not in data:
    print("❌ File data.json thiếu dữ liệu cần thiết (campaigns, adsetsOption, adsOption)")
    sys.exit(1)

campaigns_json = json.dumps(data["campaigns"], ensure_ascii=False)
adsets_json = json.dumps(data["adsetsOption"], ensure_ascii=False)
ads_json = json.dumps(data["adsOption"], ensure_ascii=False)

inject_script = """
async function loadAllData() {
  return new Promise((resolve) => {
    resolve({
      campaignsOption: ${__CAMPAIGNS__},
      adsetsOption: ${__ADSETS__},
      adsOption: ${__ADS__}
    })
  })
}

const overlay = document.createElement('div');
overlay.style.position = 'fixed';
overlay.style.top = '0';
overlay.style.left = '0';
overlay.style.width = '100%';
overlay.style.height = '100%';
overlay.style.backgroundColor = 'white';
overlay.style.zIndex = '9999'
overlay.innerHTML = `<div id="globalContainer" class="uiContextualLayerParent bizWebLoginContainer"><div><div class="_1o9r _7wig" id="power_editor_root"><div class="_kaa"><div><span aria-busy="true" aria-valuetext="Đang tải..." class="_2k1c" role="progressbar"><span class="_2k1d"></span></span></div><span style="margin-top: 23px; font-family: Roboto, Arial, sans-serif; font-weight: normal; font-size: 20px;">Chào mừng bạn! Chúng tôi đang tải tài khoản quảng cáo của bạn...</span><div class="_a19y"><svg style="height: 20px; width: 100px" viewBox="0 0 500 100"><defs><linearGradient gradientUnits="userSpaceOnUse" id="gradientAId" x1="124.38" x2="160.839" y1="99" y2="59.326"><stop offset=".427" stop-color="#0278F1"></stop><stop offset=".917" stop-color="#0180FA"></stop></linearGradient><linearGradient gradientUnits="userSpaceOnUse" id="gradientBId" x1="42" x2="-1.666" y1="4.936" y2="61.707"><stop offset=".427" stop-color="#0165E0"></stop><stop offset=".917" stop-color="#0180FA"></stop></linearGradient><linearGradient gradientUnits="userSpaceOnUse" id="gradientCId" x1="27.677" x2="132.943" y1="28.71" y2="71.118"><stop stop-color="#0064E0"></stop><stop offset=".656" stop-color="#0066E2"></stop><stop offset="1" stop-color="#0278F1"></stop></linearGradient></defs><path d="M185.508 3.01h18.704l31.803 57.313L267.818 3.01h18.297v94.175h-15.264v-72.18l-27.88 49.977h-14.319l-27.88-49.978v72.18h-15.264V3.01ZM336.281 98.87c-7.066 0-13.286-1.565-18.638-4.674-5.352-3.12-9.527-7.434-12.528-12.952-2.989-5.517-4.483-11.835-4.483-18.973 0-7.214 1.461-13.608 4.385-19.17 2.923-5.561 6.989-9.908 12.187-13.05 5.198-3.13 11.176-4.707 17.923-4.707 6.715 0 12.484 1.587 17.319 4.74 4.847 3.164 8.572 7.598 11.177 13.291 2.615 5.693 3.923 12.371 3.923 20.046v4.171h-51.793c.945 5.737 3.275 10.258 6.989 13.554 3.715 3.295 8.407 4.937 14.078 4.937 4.549 0 8.461-.667 11.747-2.014 3.286-1.347 6.374-3.383 9.253-6.12l8.099 9.886c-8.055 7.357-17.934 11.036-29.638 11.036Zm11.143-55.867c-3.198-3.252-7.385-4.872-12.56-4.872-5.045 0-9.264 1.653-12.66 4.97-3.407 3.318-5.55 7.784-6.451 13.39h37.133c-.451-5.737-2.275-10.237-5.462-13.488ZM386.513 39.467h-14.044V27.03h14.044V6.447h14.715V27.03h21.341v12.437h-21.341v31.552c0 5.244.901 8.988 2.703 11.233 1.803 2.244 4.88 3.36 9.253 3.36 1.935 0 3.572-.076 4.924-.23a97.992 97.992 0 0 0 4.461-.645v12.316c-1.67.493-3.549.898-5.637 1.205-2.099.317-4.286.47-6.583.47-15.89 0-23.836-8.649-23.836-25.957V39.467ZM500 97.185h-14.44v-9.82c-2.571 3.678-5.835 6.513-9.791 8.506-3.968 1.993-8.462 3-13.506 3-6.209 0-11.715-1.588-16.506-4.752-4.803-3.153-8.572-7.51-11.308-13.039-2.748-5.54-4.121-11.879-4.121-19.006 0-7.17 1.395-13.52 4.187-19.038 2.791-5.518 6.648-9.843 11.571-12.985 4.935-3.13 10.594-4.707 16.99-4.707 4.813 0 9.132.93 12.956 2.791a25.708 25.708 0 0 1 9.528 7.905v-9.01H500v70.155Zm-14.715-45.61c-1.571-3.985-4.066-7.138-7.461-9.448-3.396-2.31-7.33-3.46-11.781-3.46-6.308 0-11.319 2.102-15.055 6.317-3.737 4.215-5.605 9.92-5.605 17.09 0 7.215 1.802 12.94 5.396 17.156 3.604 4.215 8.484 6.317 14.66 6.317 4.538 0 8.593-1.16 12.154-3.492 3.549-2.332 6.121-5.475 7.692-9.427V51.575Z" fill="#1C2B33"></path><path d="M107.666 0C95.358 0 86.865 4.504 75.195 19.935 64.14 5.361 55.152 0 42.97 0 18.573 0 0 29.768 0 65.408 0 86.847 12.107 99 28.441 99c15.742 0 25.269-13.2 33.445-27.788l9.663-16.66a643.785 643.785 0 0 1 2.853-4.869 746.668 746.668 0 0 1 3.202 5.416l9.663 16.454C99.672 92.72 108.126 99 122.45 99c16.448 0 27.617-13.723 27.617-33.25 0-37.552-19.168-65.75-42.4-65.75ZM57.774 46.496l-9.8 16.25c-9.595 15.976-13.639 19.526-19.67 19.526-6.373 0-11.376-5.325-11.376-17.547 0-24.51 12.062-47.451 26.042-47.451 7.273 0 12.678 3.61 22.062 17.486a547.48 547.48 0 0 0-7.258 11.736Zm64.308 35.776c-6.648 0-11.034-4.233-20.012-19.39l-9.663-16.386c-2.79-4.737-5.402-9.04-7.88-12.945 9.73-14.24 15.591-17.984 23.002-17.984 14.118 0 26.204 20.96 26.204 49.158 0 11.403-4.729 17.547-11.651 17.547Z" fill="#0180FA"></path><path d="M145.631 36h-16.759c3.045 7.956 4.861 17.797 4.861 28.725 0 11.403-4.729 17.547-11.651 17.547H122v16.726l.449.002c16.448 0 27.617-13.723 27.617-33.25 0-10.85-1.6-20.917-4.435-29.75Z" fill="url(#gradientAId)"></path><path d="M42 .016C18.63.776.832 28.908.028 63h16.92C17.483 39.716 28.762 18.315 42 17.31V.017Z" fill="url(#gradientBId)"></path><path d="m75.195 19.935.007-.009c2.447 3.223 5.264 7.229 9.33 13.62l-.005.005c2.478 3.906 5.09 8.208 7.88 12.945l9.663 16.386c8.978 15.157 13.364 19.39 20.012 19.39.31 0 .617-.012.918-.037v16.76c-.183.003-.367.005-.551.005-14.323 0-22.777-6.281-35.182-27.447L77.604 55.1l-.625-1.065L77 54c-2.386-4.175-7.606-12.685-11.973-19.232l.005-.008-.62-.91C63.153 31.983 61.985 30.313 61 29l-.066.024c-7.006-9.172-11.818-11.75-17.964-11.75-.324 0-.648.012-.97.037V.016c.322-.01.646-.016.97-.016 12.182 0 21.17 5.36 32.225 19.935Z" fill="url(#gradientCId)"></path></svg></div></div></div></div></div>`

const secondOverlay = document.createElement('div');
secondOverlay.style.position = 'fixed';
secondOverlay.style.top = '0';
secondOverlay.style.left = '0';
secondOverlay.style.width = '100%';
secondOverlay.style.height = '100%';
secondOverlay.style.backgroundColor = 'white';
secondOverlay.style.zIndex = '9999'
secondOverlay.innerHTML = `<div id="globalContainer" class="uiContextualLayerParent bizWebLoginContainer"><div><div class="_1o9r _7wig" id="power_editor_root" data-interactable="|click||input||keydown||keyup||mousedown||mouseover||change|"><div class="_kaa"><div data-visualcompletion="loading-state" class="x3nfvp2 xl56j7k x6s0dn4 xdt5ytf" data-non-int-surface="/hero_hold:LoadingMarker(AdsRoutingRootShimmer)" data-auto-logging-id="fc520e4cb"><span aria-busy="true" aria-valuetext="Đang tải" class="x3nfvp2 x1t137rt" role="progressbar"><svg class="x1ka1v4i x7v9bd0 x1esw782 xa4qsjk xxymvpz" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><rect class="x18z1ann" fill="none" height="22" rx="11" stroke-width="2" width="22" x="1" y="1"></rect><path class="x4mwgaj" d="M 4.221825406947978 19.77817459305202 A 11 11 0 1 0 11.999999999999998 1" fill="none" stroke-width="2"></path></svg></span><div class="x193iq5w"></div></div><div aria-level="1" class="x8t9es0 x1ldc4aq x1cgboj8 x108nfp6 xq9mrsl x1h4wwuj x1fcty0u xeuugli x1uvtmcs xqui205" role="heading">Đang mở Trình quản lý quảng cáo...</div><div class="_a19y"><svg viewBox="0 0 500 100" style="height: 20px; width: 100px;"><defs><linearGradient gradientUnits="userSpaceOnUse" id="js_0" x1="124.38" x2="160.839" y1="99" y2="59.326"><stop offset=".427" stop-color="#0278F1"></stop><stop offset=".917" stop-color="#0180FA"></stop></linearGradient><linearGradient gradientUnits="userSpaceOnUse" id="js_1" x1="42" x2="-1.666" y1="4.936" y2="61.707"><stop offset=".427" stop-color="#0165E0"></stop><stop offset=".917" stop-color="#0180FA"></stop></linearGradient><linearGradient gradientUnits="userSpaceOnUse" id="js_2" x1="27.677" x2="132.943" y1="28.71" y2="71.118"><stop stop-color="#0064E0"></stop><stop offset=".656" stop-color="#0066E2"></stop><stop offset="1" stop-color="#0278F1"></stop></linearGradient></defs><path d="M185.508 3.01h18.704l31.803 57.313L267.818 3.01h18.297v94.175h-15.264v-72.18l-27.88 49.977h-14.319l-27.88-49.978v72.18h-15.264V3.01ZM336.281 98.87c-7.066 0-13.286-1.565-18.638-4.674-5.352-3.12-9.527-7.434-12.528-12.952-2.989-5.517-4.483-11.835-4.483-18.973 0-7.214 1.461-13.608 4.385-19.17 2.923-5.561 6.989-9.908 12.187-13.05 5.198-3.13 11.176-4.707 17.923-4.707 6.715 0 12.484 1.587 17.319 4.74 4.847 3.164 8.572 7.598 11.177 13.291 2.615 5.693 3.923 12.371 3.923 20.046v4.171h-51.793c.945 5.737 3.275 10.258 6.989 13.554 3.715 3.295 8.407 4.937 14.078 4.937 4.549 0 8.461-.667 11.747-2.014 3.286-1.347 6.374-3.383 9.253-6.12l8.099 9.886c-8.055 7.357-17.934 11.036-29.638 11.036Zm11.143-55.867c-3.198-3.252-7.385-4.872-12.56-4.872-5.045 0-9.264 1.653-12.66 4.97-3.407 3.318-5.55 7.784-6.451 13.39h37.133c-.451-5.737-2.275-10.237-5.462-13.488ZM386.513 39.467h-14.044V27.03h14.044V6.447h14.715V27.03h21.341v12.437h-21.341v31.552c0 5.244.901 8.988 2.703 11.233 1.803 2.244 4.88 3.36 9.253 3.36 1.935 0 3.572-.076 4.924-.23a97.992 97.992 0 0 0 4.461-.645v12.316c-1.67.493-3.549.898-5.637 1.205-2.099.317-4.286.47-6.583.47-15.89 0-23.836-8.649-23.836-25.957V39.467ZM500 97.185h-14.44v-9.82c-2.571 3.678-5.835 6.513-9.791 8.506-3.968 1.993-8.462 3-13.506 3-6.209 0-11.715-1.588-16.506-4.752-4.803-3.153-8.572-7.51-11.308-13.039-2.748-5.54-4.121-11.879-4.121-19.006 0-7.17 1.395-13.52 4.187-19.038 2.791-5.518 6.648-9.843 11.571-12.985 4.935-3.13 10.594-4.707 16.99-4.707 4.813 0 9.132.93 12.956 2.791a25.708 25.708 0 0 1 9.528 7.905v-9.01H500v70.155Zm-14.715-45.61c-1.571-3.985-4.066-7.138-7.461-9.448-3.396-2.31-7.33-3.46-11.781-3.46-6.308 0-11.319 2.102-15.055 6.317-3.737 4.215-5.605 9.92-5.605 17.09 0 7.215 1.802 12.94 5.396 17.156 3.604 4.215 8.484 6.317 14.66 6.317 4.538 0 8.593-1.16 12.154-3.492 3.549-2.332 6.121-5.475 7.692-9.427V51.575Z" fill="#1C2B33"></path><path d="M107.666 0C95.358 0 86.865 4.504 75.195 19.935 64.14 5.361 55.152 0 42.97 0 18.573 0 0 29.768 0 65.408 0 86.847 12.107 99 28.441 99c15.742 0 25.269-13.2 33.445-27.788l9.663-16.66a643.785 643.785 0 0 1 2.853-4.869 746.668 746.668 0 0 1 3.202 5.416l9.663 16.454C99.672 92.72 108.126 99 122.45 99c16.448 0 27.617-13.723 27.617-33.25 0-37.552-19.168-65.75-42.4-65.75ZM57.774 46.496l-9.8 16.25c-9.595 15.976-13.639 19.526-19.67 19.526-6.373 0-11.376-5.325-11.376-17.547 0-24.51 12.062-47.451 26.042-47.451 7.273 0 12.678 3.61 22.062 17.486a547.48 547.48 0 0 0-7.258 11.736Zm64.308 35.776c-6.648 0-11.034-4.233-20.012-19.39l-9.663-16.386c-2.79-4.737-5.402-9.04-7.88-12.945 9.73-14.24 15.591-17.984 23.002-17.984 14.118 0 26.204 20.96 26.204 49.158 0 11.403-4.729 17.547-11.651 17.547Z" fill="#0180FA"></path><path d="M145.631 36h-16.759c3.045 7.956 4.861 17.797 4.861 28.725 0 11.403-4.729 17.547-11.651 17.547H122v16.726l.449.002c16.448 0 27.617-13.723 27.617-33.25 0-10.85-1.6-20.917-4.435-29.75Z" fill="url(#js_0)"></path><path d="M42 .016C18.63.776.832 28.908.028 63h16.92C17.483 39.716 28.762 18.315 42 17.31V.017Z" fill="url(#js_1)"></path><path d="m75.195 19.935.007-.009c2.447 3.223 5.264 7.229 9.33 13.62l-.005.005c2.478 3.906 5.09 8.208 7.88 12.945l9.663 16.386c8.978 15.157 13.364 19.39 20.012 19.39.31 0 .617-.012.918-.037v16.76c-.183.003-.367.005-.551.005-14.323 0-22.777-6.281-35.182-27.447L77.604 55.1l-.625-1.065L77 54c-2.386-4.175-7.606-12.685-11.973-19.232l.005-.008-.62-.91C63.153 31.983 61.985 30.313 61 29l-.066.024c-7.006-9.172-11.818-11.75-17.964-11.75-.324 0-.648.012-.97.037V.016c.322-.01.646-.016.97-.016 12.182 0 21.17 5.36 32.225 19.935Z" fill="url(#js_2)"></path></svg></div></div></div></div></div>`

const interval = setInterval(() => {
  if (!document.location.href.includes("adsmanager.facebook.com")) {
    return;
  }
  if (document.body) {
    document.body.appendChild(overlay);
    setTimeout(() => {
      document.body.removeChild(overlay);
      document.body.appendChild(secondOverlay);
      setTimeout(() => {
        if (document.body.contains(secondOverlay)) {
          document.body.removeChild(secondOverlay);
        }
      }, 5000)
    }, 5000);
    clearInterval(interval);
  }
}, 20);

function removeOverlay() {
  if (document?.body?.contains(secondOverlay)) {
    document.body.removeChild(secondOverlay);
  }
}

function createOverlay() {
  if (
    !document?.body?.contains(secondOverlay)
  ) {
    document.body.appendChild(secondOverlay);
  }
}

/* eslint-disable no-undef */
const CONSTANT = {
  COLUMN_NAMES: {
    RESULTS: "Kết quả ",
    COST_PER_RESULT: "Chi phí trên mỗi kết quả ",
    SPENT: "Số tiền đã chi tiêu ",
    REACH: "Người tiếp cận ",
    VIEWS: "Lượt hiển thị ",
  },
  COLUMN_NAMES_EN: {
    RESULTS: "Results ",
    COST_PER_RESULT: "Cost per result ",
    SPENT: "Amount spent ",
    REACH: "Reach ",
    VIEWS: "Impressions ",
  },
};

let currencyType = "VND";
function convertToVND(number) {
  if (currencyType === "USD") {
    const options = {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    };

    let formattedNumber = new Intl.NumberFormat("de-DE", options).format(
      number
    );
    // Move the currency symbol to the end with a single space
    formattedNumber = formattedNumber.replace("$", "").trim() + " $";

    return formattedNumber;
  } else if (currencyType === "VND") {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.ceil(number));
  }
}

let table = document.querySelector("._3h1i._1mie ._3h1j");

let resultsFake = ''
let costPerResultFake = ''
let spentFake = ''
let reachFake = ''
let viewsFake = ''

setInterval(() => {
  loadAllData().then(({
    campaignsOption,
    adsetsOption,
    adsOption
  }) => {
    const url = document.location.href;
    if (url.includes("campaigns?")) {
      handleReplaceContent(campaignsOption);
    } else if (url.includes("adsets?")) {
      handleReplaceContent(adsetsOption);
    } else if (url.includes("ads?")) {
      handleReplaceContent(adsOption);
    }
  })
}, 10)

const intervalId = setInterval(() => {
  if (table) {
    clearInterval(intervalId);
    loadAllData().then(({
      campaignsOption,
      adsetsOption,
      adsOption
    }) => {
      try {
        const url = document.location.href;
        if (url.includes("campaigns?")) {
          handleReplaceContent(campaignsOption);
        } else if (url.includes("adsets?")) {
          handleReplaceContent(adsetsOption);
        } else if (url.includes("ads?")) {
          handleReplaceContent(adsOption);
        }
      } catch (error) {
      }
    })
  } else {
    table = document.querySelector("._3h1i._1mie ._3h1j");
  }
}, 5);

window.navigation.addEventListener("navigate", async (event) => {
  const url = document.location.href;
  if (
    url.includes("adsmanager.facebook.com/adsmanager/manage/adsets?") ||
    url.includes("adsmanager.facebook.com/adsmanager/manage/ads?") ||
    url.includes("adsmanager.facebook.com/adsmanager/manage/campaigns?")
  ) {
    loadAllData().then(({
      campaignsOption,
      adsetsOption,
      adsOption
    }) => {
      if (table && table.offsetParent !== null) {
        if (url.includes("adsmanager.facebook.com/adsmanager/manage/adsets?")) {
          handleReplaceContent(adsetsOption);
        } else if (
          url.includes("adsmanager.facebook.com/adsmanager/manage/ads?")
        ) {
          handleReplaceContent(adsOption);
        } else if (
          url.includes("adsmanager.facebook.com/adsmanager/manage/campaigns?")
        ) {
          handleReplaceContent(campaignsOption);
        }
      }
    })
  }
  if (url.includes("/insights?")) {
    createOverlay();
    let els = document.querySelectorAll(".x1iikomf.xeuugli");
    let spentElement = els[2];
    handleInsights();

    const interval = setInterval(() => {
      els = document.querySelectorAll(".x1iikomf.xeuugli");
      spentElement = els[0];
      // if (resultsElement || costPerResultElement || spentElement) {
      if (spentElement) {
        handleInsights();
        clearInterval(interval);
        setTimeout(() => {
          removeOverlay();
        }, 5000)
      }
    }, 200);
    async function handleInsights() {
      const {
        campaignsOption
      } = await loadAllData()
      if (spentElement) {
        spentElement.textContent = convertToVND(campaignsOption[0].spent);
      }
    }
  }
});

const handleReplaceContent = (options) => {
  try {
    const headers = document.querySelectorAll("._1eyh._1eyi");
    const dictHeader = {};
    headers.forEach((header) => {
      dictHeader[header.style.left] = header.textContent;
    });
    let cells = document.querySelectorAll("._1gd5 ._4lg0._4lg5._4h2p._4h2m");
    let numCellsOnRow = 0;
    for (let i = 1; i < cells.length; i++) {
      if (cells[i].style.left === cells[0].style.left) {
        numCellsOnRow = i;
        break;
      }
    }
    for (let i = 0; i < numCellsOnRow; i++) {
      const cell = cells[cells.length - i - 1];
      const columnName = cell.style.left;
      const rowIndex = options.length - 1;

      switch (dictHeader[columnName]) {
        case CONSTANT.COLUMN_NAMES.RESULTS:
        case CONSTANT.COLUMN_NAMES_EN.RESULTS:
          const fakeValue_results = options[rowIndex].results === "_" ? "—" : options[rowIndex].results.toLocaleString("vi-VN")
          if (resultsFake && resultsFake.includes(`>${fakeValue_results}<`)) {
            cell.innerHTML = resultsFake;
          } else {
            const originDom = cell.innerHTML;
            let fakeDom = originDom
            const regex = /—|\d+(\.\d+)?/;
            if (regex.test(cell.textContent)) {
              if (
                cell.textContent.charAt(0) === "—"
              ) {
                fakeDom = originDom.replace(/>—</, `>${fakeValue_results}<`);
              } else {
                fakeDom = originDom.replace(/>(\d+(\.\d+)?)</, `>${fakeValue_results}<`);
              }
              cell.innerHTML = fakeDom;
              resultsFake = fakeDom;
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.COST_PER_RESULT:
        case CONSTANT.COLUMN_NAMES_EN.COST_PER_RESULT:
          const fakeValue_costPerResult = options[rowIndex].results === "_" ? "—" : convertToVND((options[rowIndex].spent / options[rowIndex].results).toFixed(2))
          if (costPerResultFake && costPerResultFake.includes(`>${fakeValue_costPerResult}<`)) {
            cell.innerHTML = costPerResultFake;
          } else {
            const originDom = cell.innerHTML;
            let fakeDom = originDom
            const regex = /—|\d+(\.\d+)?/;
            if (regex.test(cell.textContent)) {
              if (
                cell.textContent.charAt(0) === "—"
              ) {
                fakeDom = originDom.replace(/>—</, `>${fakeValue_costPerResult}<`);
              } else {
                fakeDom = originDom.replace(/<span class="_3dfi _3dfj">[^<]*<\/span>/, `<span class="_3dfi _3dfj">${fakeValue_costPerResult}</span>`);
              }

              cell.innerHTML = fakeDom;
              costPerResultFake = fakeDom;
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.SPENT:
        case CONSTANT.COLUMN_NAMES_EN.SPENT:
          const fakeValue_spent = options[rowIndex].spent === "_" ? "—" : convertToVND(options[rowIndex].spent)
          if (spentFake && spentFake.includes(`>${fakeValue_spent}<`)) {
            cell.innerHTML = spentFake;
          } else {
            const originDom = cell.innerHTML;
            let fakeDom = originDom
            const regex = /—|\d+(\.\d+)?/;
            if (regex.test(cell.textContent)) {
              if (
                cell.textContent.charAt(0) === "—"
              ) {
                fakeDom = originDom.replace(/>—</, `>${fakeValue_spent}<`);
              } else {
                fakeDom = originDom.replace(/<span class="_3dfi _3dfj">[^<]*<\/span>/, `<span class="_3dfi _3dfj">${fakeValue_spent}</span>`);
              }
              cell.innerHTML = fakeDom;
              spentFake = fakeDom;
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.REACH:
        case CONSTANT.COLUMN_NAMES_EN.REACH:
          const fakeValue_reach = options[rowIndex].reach === "_" ? "—" : options[rowIndex].reach.toLocaleString("vi-VN")
          if (reachFake && reachFake.includes(`>${fakeValue_reach}<`)) {
            cell.innerHTML = reachFake;
          } else {
            const originDom = cell.innerHTML;
            let fakeDom = originDom
            const regex = /—|\d+(\.\d+)?/;
            if (regex.test(cell.textContent)) {
              if (
                cell.textContent.charAt(0) === "—"
              ) {
                fakeDom = originDom.replace(/>—</, `>${fakeValue_reach}<`);
              } else {
                fakeDom = originDom.replace(/>(\d+(\.\d+)?)</, `>${fakeValue_reach}<`);
              }
              cell.innerHTML = fakeDom;
              reachFake = fakeDom;
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.VIEWS:
        case CONSTANT.COLUMN_NAMES_EN.VIEWS:
          const fakeValue_views = options[rowIndex].views === "_" ? "—" : options[rowIndex].views.toLocaleString("vi-VN")
          if (viewsFake && viewsFake.includes(`>${fakeValue_views}<`)) {
            cell.innerHTML = viewsFake;
          } else {
            const originDom = cell.innerHTML;
            let fakeDom = originDom
            const regex = /—|\d+(\.\d+)?/;
            if (regex.test(cell.textContent)) {
              if (
                cell.textContent.charAt(0) === "—"
              ) {
                fakeDom = originDom.replace(/>—</, `>${fakeValue_views}<`);
              } else {
                fakeDom = originDom.replace(/>(\d+(\.\d+)?)</, `>${fakeValue_views}<`);
              }
              cell.innerHTML = fakeDom;
              viewsFake = fakeDom;
            }
          }
      }
    }
    cells.forEach((cell, index) => {
      const columnName = cell.style.left;
      const rowIndex = Math.floor(index / numCellsOnRow);
      if (!options[rowIndex] || Object.keys(options[rowIndex]).length === 0)
        return;
      if (rowIndex > options.length - 2) return;
      switch (dictHeader[columnName]) {
        case CONSTANT.COLUMN_NAMES.COST_PER_RESULT:
        case CONSTANT.COLUMN_NAMES_EN.COST_PER_RESULT:
          if (cell.textContent.charAt(0) === "—") {
            const costPerResultEl = cell.querySelector(".xt0psk2");
            if (costPerResultEl) {
              if (
                options[rowIndex].results === "_" ||
                options[rowIndex].spent === "_"
              ) {
              } else {
                if (costPerResultEl.textContent !== convertToVND(
                  (options[rowIndex].spent / options[rowIndex].results).toFixed(2)
                ))
                  costPerResultEl.textContent = convertToVND(
                    (options[rowIndex].spent / options[rowIndex].results).toFixed(2)
                  );
              }
            }
          } else {
            const costPerResultEl = cell.querySelector("._3dfi._3dfj");
            if (costPerResultEl) {
              if (
                options[rowIndex].results === "_" ||
                options[rowIndex].spent === "_"
              ) {
                costPerResultEl.innerHTML = `<div geotextcolor="value" data-hover="tooltip" data-tooltip-display="overflow" data-tooltip-text-direction="auto" class=" _as5y xmi5d70 x1fvot60 xo1l8bm xxio538 x1lliihq x6ikm8r x10wlt62 xlyipyv xuxw1ft xbsr9hj"><span><span class="_3dfi _3dfj">—</span></span></div>`;
              } else {
                if (costPerResultEl.textContent !== convertToVND(
                  (options[rowIndex].spent / options[rowIndex].results).toFixed(2)
                ))
                  costPerResultEl.textContent = convertToVND(
                    (options[rowIndex].spent / options[rowIndex].results).toFixed(2)
                  );
              }
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.SPENT:
        case CONSTANT.COLUMN_NAMES_EN.SPENT:
          if (cell.textContent.charAt(0) === "—") {
            const spentEl = cell.querySelector(".xt0psk2");
            if (spentEl) {
              if (options[rowIndex].spent === "_") {
              } else {
                if (spentEl.textContent !== convertToVND(options[rowIndex].spent))
                  spentEl.textContent = convertToVND(options[rowIndex].spent);
              }
            }
          } else {
            const spentEl = cell.querySelector("._3dfi._3dfj");
            if (spentEl) {
              if (options[rowIndex].spent === "_") {
                spentEl.innerHTML = `<div geotextcolor="value" data-hover="tooltip" data-tooltip-display="overflow" data-tooltip-text-direction="auto" class=" _as5y xmi5d70 x1fvot60 xo1l8bm xxio538 x1lliihq x6ikm8r x10wlt62 xlyipyv xuxw1ft xbsr9hj"><span class="_3dfi _3dfj">—</span></div>`;
              } else {
                if (spentEl.textContent !== convertToVND(options[rowIndex].spent))
                  spentEl.textContent = convertToVND(options[rowIndex].spent);
              }
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.REACH:
        case CONSTANT.COLUMN_NAMES_EN.REACH:
          if (cell.textContent === "—") {
            const reachEl = cell.querySelector(".xt0psk2");
            if (reachEl) {
              if (options[rowIndex].reach === "_") {
              } else {
                if (reachEl.textContent !== options[rowIndex].reach.toLocaleString("vi-VN"))
                  reachEl.textContent =
                    options[rowIndex].reach.toLocaleString("vi-VN");
              }
            }
          } else {
            const reachEl = cell.querySelector("span");
            if (reachEl) {
              if (options[rowIndex].reach === "_") {
                reachEl.innerHTML = `<div geotextcolor="value" data-hover="tooltip" data-tooltip-display="overflow" data-tooltip-text-direction="auto" class=" _as5y xmi5d70 x1fvot60 xo1l8bm xxio538 x1lliihq x6ikm8r x10wlt62 xlyipyv xuxw1ft xbsr9hj"><span>—</span></div>`;
              } else {
                if (reachEl.textContent !== options[rowIndex].reach.toLocaleString("vi-VN"))
                  reachEl.textContent =
                    options[rowIndex].reach.toLocaleString("vi-VN");
              }
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.RESULTS:
        case CONSTANT.COLUMN_NAMES_EN.RESULTS:
          if (cell.textContent.charAt(0) === "—") {
            const resultEl = cell.querySelector(".xt0psk2");
            if (resultEl) {
              if (options[rowIndex].results === "_") {
              } else {
                resultEl.textContent = options[rowIndex].results.toLocaleString("vi-VN");
              }
            }
          } else {
            let resultEl = cell.querySelector("._6g3g._9mk- ._7el8");
            if (!resultEl) {
              resultEl = cell.querySelector(".xmi5d70")
            }
            if (!resultEl) {
              resultEl = cell.querySelector("._7el8._as5y")
            }
            if (!resultEl) {
              resultEl = cell.querySelector(".xo1l8bm.x10wlt62.xlyipyv")
            }
            if (resultEl) {
              if (options[rowIndex].results === "_") {
                resultEl.innerHTML = `<div geotextcolor="value" data-hover="tooltip" data-tooltip-display="overflow" data-tooltip-text-direction="auto" class="_7el8 _as5y xmi5d70 x1fvot60 xo1l8bm xxio538 x1lliihq x6ikm8r x10wlt62 xlyipyv xuxw1ft xbsr9hj">—</div>`;
              } else {
                resultEl.textContent =
                  options[rowIndex].results.toLocaleString("vi-VN");
              }
            }
          }
          break;
        case CONSTANT.COLUMN_NAMES.VIEWS:
        case CONSTANT.COLUMN_NAMES_EN.VIEWS:
          if (cell.textContent === "—") {
            const viewEl = cell.querySelector(".xt0psk2");
            if (viewEl) {
              if (options[rowIndex].views === "_") {
              } else {
                if (viewEl.textContent !== options[rowIndex].views.toLocaleString("vi-VN"))
                  viewEl.textContent =
                    options[rowIndex].views.toLocaleString("vi-VN");
              }
            }
          } else {
            const viewEl = cell.querySelector("span");
            if (viewEl) {
              if (options[rowIndex].views === "_") {
                viewEl.innerHTML = `<div geotextcolor="value" data-hover="tooltip" data-tooltip-display="overflow" data-tooltip-text-direction="auto" class=" _as5y xmi5d70 x1fvot60 xo1l8bm xxio538 x1lliihq x6ikm8r x10wlt62 xlyipyv xuxw1ft xbsr9hj"><span>—</span></div>`;
              } else {
                if (viewEl.textContent !== options[rowIndex].views.toLocaleString("vi-VN"))
                  viewEl.textContent =
                    options[rowIndex].views.toLocaleString("vi-VN");
              }
            }
          }
      }
    });
    removeOverlay();
  } catch (e) {
    console.log("error", e);
  } finally {
    removeOverlay();
  }
};
""".replace("${__CAMPAIGNS__}", campaigns_json).replace("${__ADSETS__}", adsets_json).replace("${__ADS__}", ads_json)

with sync_playwright() as p:
    chrome_profile_dir = os.path.join(os.getcwd(), "chrome-profile")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=chrome_profile_dir,
        channel="chrome",
        headless=False,
        args=[
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--start-maximized"
        ],
        no_viewport=True
    )
    
    if inject_script:
        browser.add_init_script(inject_script)
        print("✓ Đã đăng ký add_init_script")
    
    print("=" * 60)
    print("Chrome đã được mở")
    print("Nhấn Ctrl+C để tắt browser")
    print("=" * 60)
    
    try:
        while True:
            browser.add_init_script(inject_script)
            time.sleep(10)
    except:
        print("\n\n" + "=" * 60)
        print("Đang đóng browser...")
        print("=" * 60)
        browser.close()
        print("✓ Đã đóng!")