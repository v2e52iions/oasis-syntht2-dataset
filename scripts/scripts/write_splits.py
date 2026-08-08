"""Write deterministic subject split lists for OASIS and OASIS-SynthT2."""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dataset import split_subjects
from utils.dataset_synth import split_synth_subjects


def write_list(path: str, subjects) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for subject in subjects:
            handle.write(os.path.basename(subject) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oasis_dir", required=True)
    parser.add_argument("--out_dir", default="metadata")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    for split in ("train", "val", "test"):
        write_list(os.path.join(args.out_dir, f"oasis_{split}.txt"), split_subjects(args.oasis_dir, split))
        write_list(os.path.join(args.out_dir, f"syntht2_{split}.txt"), split_synth_subjects(args.oasis_dir, split))

    print(f"Wrote split files to {args.out_dir}")


if __name__ == "__main__":
    main()
