#!/usr/bin/env python3
"""
Download GeoJSON files for US states and Canadian provinces and save them to the current
`tableau/` folder (where this script lives).

Usage:
    python download_geojsons.py

The script will prefer local files (if present) and otherwise try a small list of public URLs.
It will save files as:
    - us_states.geojson
    - canada_provinces.geojson

If `requests` is available the script uses it; otherwise falls back to urllib.
"""

from pathlib import Path
import json
import os
import sys

try:
    import requests
except Exception:
    requests = None

import urllib.request


def _download_text(url, timeout=15):
    if requests is not None:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    else:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8")


def try_urls_save(local_path: Path, urls):
    """Try the provided urls in order and save the first successful JSON to local_path.
    Returns True on success, False otherwise.
    """
    if local_path.exists():
        print(f"[skip] {local_path} already exists")
        return True

    for url in urls:
        print(f"Trying {url} ...")
        try:
            text = _download_text(url)
            # validate JSON
            data = json.loads(text)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            # write pretty JSON
            local_path.write_text(json.dumps(data))
            print(f"Saved {local_path}")
            return True
        except Exception as e:
            print(f"  failed: {e}")
    print(f"All URLs failed for {local_path}")
    return False


def main():
    here = Path(__file__).resolve().parent
    us_dest = here / "us_states.geojson"
    ca_dest = here / "canada_provinces.geojson"

    us_urls = [
        # PublicaMundi (common source for US states)
        "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
        # folium example dataset
        "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json",
    ]

    ca_urls = [
        # codeforgermany / click_that_hood
        "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada-provinces.geojson",
        "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/canada-provinces.geojson",
    ]

    ok_us = try_urls_save(us_dest, us_urls)
    ok_ca = try_urls_save(ca_dest, ca_urls)

    if not ok_us:
        print("US states GeoJSON not available. You can provide a file named us_states.geojson in the tableau/ folder.")
    if not ok_ca:
        print("Canada provinces GeoJSON not available. You can provide a file named canada_provinces.geojson in the tableau/ folder.")

    if ok_us or ok_ca:
        print("Done.")
    else:
        print("No GeoJSON downloaded.")


if __name__ == '__main__':
    main()
