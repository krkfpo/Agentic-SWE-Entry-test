import json
import sys
import urllib.error
import urllib.request


def fetch(url):
    """Return parsed JSON, or None if PyPI answers 404."""
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def main(path="requirements.txt"):
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]

    missing_pkgs = 0
    missing_versions = 0
    oldest = None  # (upload_time, name, version)

    for line in lines:
        name, version = line.split("==", 1)
        if fetch(f"https://pypi.org/pypi/{name}/json") is None:
            missing_pkgs += 1
            continue
        release = fetch(f"https://pypi.org/pypi/{name}/{version}/json")
        if release is None:
            missing_versions += 1
            continue
        files = release.get("urls", [])
        if not files:
            continue
        t = files[0]["upload_time"]  # first file under urls
        if oldest is None or t < oldest[0]:
            oldest = (t, name, version)

    print(f"Dependencies checked: {len(lines)}")
    print(f"Packages not on PyPI: {missing_pkgs}")
    print(f"Versions not on PyPI: {missing_versions}")
    if oldest:
        print(f"Oldest pinned release: {oldest[1]}=={oldest[2]} ({oldest[0][:4]})")
    else:
        print("Oldest pinned release: none")


if __name__ == "__main__":
    main(*sys.argv[1:])