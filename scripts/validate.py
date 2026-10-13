import hashlib
import io
import json
import re
import struct
import urllib.request
import zipfile
from pathlib import Path


manifest = json.loads(Path("bucket/herdr-gpui.json").read_text())
version = manifest["version"]
assert re.fullmatch(r"\d{8}\.\d+", version), "Invalid release version"
assert manifest["bin"] == [["conhost.exe", "herdr-gpui", '--headless "$dir\\herdr-gpui.exe"']]
assert manifest["shortcuts"] == [["..\\..\\..\\shims\\herdr-gpui.exe", "Herdr", "", "icons\\herdr.ico"]]
assert manifest["depends"] == "rcedit"
assert manifest["license"] == "Apache-2.0"
assert set(manifest["architecture"]) == {"64bit", "arm64"}

icon = Path("scripts/herdr-gpui/herdr.ico").read_bytes()
assert struct.unpack_from("<HHH", icon) == (0, 1, 7), "Invalid ICO header"
for index, size in enumerate([16, 24, 32, 48, 64, 128, 256]):
    width, height, _, _, planes, bits, length, offset = struct.unpack_from("<BBBBHHII", icon, 6 + index * 16)
    assert (width or 256, height or 256, planes, bits) == (size, size, 1, 32)
    png = icon[offset:offset + length]
    assert len(png) == length and png[:8] == b"\x89PNG\r\n\x1a\n", "Invalid ICO image"
    assert struct.unpack_from(">II", png, 16) == (size, size), "ICO image dimensions mismatch"
print("Herdr icon: all seven resolutions verified")

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
