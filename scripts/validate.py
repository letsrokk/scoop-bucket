import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path


manifest = json.loads(Path("bucket/herdr-gpui.json").read_text())
version = manifest["version"]
assert re.fullmatch(r"\d{8}\.\d+", version), "Invalid release version"
assert manifest["bin"] == "herdr-gpui.exe"
assert manifest["shortcuts"] == [["herdr-gpui.exe", "Herdr"]]
assert manifest["license"] == "Apache-2.0"
assert set(manifest["architecture"]) == {"64bit", "arm64"}

for architecture, target in {"64bit": "x86_64", "arm64": "aarch64"}.items():
    package = manifest["architecture"][architecture]
    directory = f"Herdr-{version}-{target}-pc-windows-msvc"
    url = f"https://github.com/penso/herdr-gpui/releases/download/v{version}/{directory}.zip"
    assert package["url"] == url, f"{architecture}: URL/version mismatch"
    assert package["extract_dir"] == directory, f"{architecture}: extraction directory mismatch"
    assert re.fullmatch(r"[a-f0-9]{64}", package["hash"]), f"{architecture}: invalid SHA-256"
    with urllib.request.urlopen(url, timeout=120) as response:
        archive = response.read()
    assert hashlib.sha256(archive).hexdigest() == package["hash"], f"{architecture}: checksum mismatch"
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        assert f"{directory}/herdr-gpui.exe" in zipped.namelist(), f"{architecture}: executable missing"
        assert zipped.testzip() is None, f"{architecture}: corrupt ZIP"
    print(f"{architecture}: version, checksum, and executable verified")
