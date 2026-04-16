#!/usr/bin/env python3
"""Download the eBird Basic Dataset from SWITCHdrive into data/ebird/.
AUTHOR: Marc Vogelmann
"""

import os
import sys
import zipfile
import urllib.request

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
LINK_FILE = os.path.join(BASE_DIR, "data", "link.url")
DATA_DIR = os.path.join(BASE_DIR, "data", "ebird")

with open(LINK_FILE, encoding="utf-8") as f:
    SHARE_URL = f.read().strip()
DOWNLOAD_URL = f"{SHARE_URL}/download"
ZIP_PATH = os.path.join(DATA_DIR, "ebird_download.zip")


def download(url: str, dest: str) -> None:
    """Download a file from *url* to *dest* with progress reporting."""
    print(f"Downloading from {url} ...")

    def _progress(block_num: int, block_size: int, total_size: int) -> None:
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100, downloaded * 100 / total_size)
            mb = downloaded / 1_048_576
            total_mb = total_size / 1_048_576
            sys.stdout.write(f"\r  {pct:5.1f}%  ({mb:.1f} / {total_mb:.1f} MB)")
        else:
            mb = downloaded / 1_048_576
            sys.stdout.write(f"\r  {mb:.1f} MB downloaded")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest, reporthook=_progress)
    print()  # newline after progress


def extract(zip_path: str, dest_dir: str) -> None:
    """Extract a zip archive into *dest_dir*."""
    print(f"Extracting to {os.path.abspath(dest_dir)} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    print(f"  Extracted {len(zipfile.ZipFile(zip_path).namelist())} files.")


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    # Download
    download(DOWNLOAD_URL, ZIP_PATH)

    # Extract
    extract(ZIP_PATH, DATA_DIR)

    # Clean up zip
    os.remove(ZIP_PATH)
    print("Done. Downloaded eBird data is in data/ebird/.")


if __name__ == "__main__":
    main()
