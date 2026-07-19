# -*- coding: utf-8 -*-
"""Encrypted local store — giữ data khỏi thư mục EXE / mắt người dùng."""

from __future__ import annotations

import base64
import json
import os
import shutil
import sys
from typing import Any, Dict, Optional

APP_DIR_NAME = "QuanLyFB"
STORE_FILENAME = "store.bin"
LEGACY_FILENAME = "data.json"

_DEFAULT = {
    "licenseKey": "",
    "campaigns": [],
    "adsetsOption": [],
    "adsOption": [],
}


def app_data_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def store_path() -> str:
    return os.path.join(app_data_dir(), STORE_FILENAME)


def chrome_profile_dir() -> str:
    path = os.path.join(app_data_dir(), "chrome-profile")
    os.makedirs(path, exist_ok=True)
    return path


def default_data() -> Dict[str, Any]:
    return json.loads(json.dumps(_DEFAULT))


def _exe_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _find_legacy_json() -> Optional[str]:
    candidates = [
        os.path.join(os.getcwd(), LEGACY_FILENAME),
        os.path.join(_exe_dir(), LEGACY_FILENAME),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _fernet():
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    except ImportError:
        return None

    try:
        from security import get_identifier

        material = get_identifier() or "offline"
    except Exception:
        material = "offline"

    salt = b"QuanLyFB-store-v1"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=120_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(material.encode("utf-8")))
    return Fernet(key)


def _encrypt(payload: bytes) -> bytes:
    f = _fernet()
    if f is None:
        # Fallback plaintext marker — vẫn nằm AppData, không cạnh EXE
        return b"PLAIN:" + payload
    return b"ENC1:" + f.encrypt(payload)


def _decrypt(blob: bytes) -> bytes:
    if blob.startswith(b"PLAIN:"):
        return blob[6:]
    if blob.startswith(b"ENC1:"):
        f = _fernet()
        if f is None:
            raise RuntimeError("Thiếu cryptography để đọc store")
        return f.decrypt(blob[5:])
    # File cũ / lạ: thử giải mã trực tiếp
    f = _fernet()
    if f is None:
        return blob
    return f.decrypt(blob)


def load_store() -> Dict[str, Any]:
    path = store_path()
    if os.path.isfile(path):
        try:
            with open(path, "rb") as f:
                raw = _decrypt(f.read())
            data = json.loads(raw.decode("utf-8"))
            if isinstance(data, dict):
                merged = default_data()
                merged.update(data)
                for key in ("campaigns", "adsetsOption", "adsOption"):
                    if not isinstance(merged.get(key), list):
                        merged[key] = []
                return merged
        except Exception:
            pass

    legacy = _find_legacy_json()
    if legacy:
        try:
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                merged = default_data()
                merged.update(data)
                save_store(merged)
                return merged
        except Exception:
            pass

    return default_data()


def save_store(data: Dict[str, Any]) -> bool:
    path = store_path()
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    blob = _encrypt(payload)
    tmp = path + ".tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(blob)
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        return False


def migrate_chrome_profile_if_needed() -> None:
    """Chuyển chrome-profile cạnh EXE/cwd vào AppData nếu chưa có."""
    dest = chrome_profile_dir()
    if os.listdir(dest):
        return
    for src in (
        os.path.join(os.getcwd(), "chrome-profile"),
        os.path.join(_exe_dir(), "chrome-profile"),
    ):
        if os.path.isdir(src) and os.path.abspath(src) != os.path.abspath(dest):
            try:
                for name in os.listdir(src):
                    s = os.path.join(src, name)
                    d = os.path.join(dest, name)
                    if os.path.exists(d):
                        continue
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                return
            except Exception:
                continue
