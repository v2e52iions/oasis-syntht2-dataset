"""Download helper for the public Learn2Reg OASIS dataset.

The original MRI data are not redistributed in this repository. This script
only points users to the public Learn2Reg OASIS package.
"""

import argparse
import os
import urllib.request
import zipfile


LEARN2REG_OASIS_URL = "https://cloud.imi.uni-luebeck.de/s/mFnRMzjpSSLbzxm/download"


def download_learn2reg_oasis(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, "OASIS_L2R.zip")

    print("Downloading the public Learn2Reg OASIS dataset.")
    print("If download is slow, copy this URL into a browser or download manager:")
    print(f"  {LEARN2REG_OASIS_URL}")
    print(f"Destination: {zip_path}")

    def progress(count: int, block_size: int, total_size: int) -> None:
        if total_size <= 0:
            return
        pct = count * block_size / total_size * 100
        print(f"\r  {pct:.1f}%", end="", flush=True)

    urllib.request.urlretrieve(LEARN2REG_OASIS_URL, zip_path, progress)
    print("\nExtracting archive...")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(out_dir)
    os.remove(zip_path)
    print(f"Done. Extracted data under: {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", default="data/oasis_raw")
    args = parser.parse_args()
    download_learn2reg_oasis(args.out_dir)
