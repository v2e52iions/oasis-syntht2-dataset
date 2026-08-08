"""Materialize synthetic T2-like NIfTI slices from OASIS T1 slices."""

import argparse
import os
import sys

import nibabel as nib
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dataset_synth import split_synth_subjects, synth_t2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oasis_dir", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--seed_offset", type=int, default=1000)
    args = parser.parse_args()

    subjects = []
    for split in ("train", "val", "test"):
        subjects.extend(split_synth_subjects(args.oasis_dir, split))

    os.makedirs(args.out_dir, exist_ok=True)

    for idx, subject in enumerate(subjects):
        subject_name = os.path.basename(subject)
        t1_path = os.path.join(subject, "slice_norm.nii.gz")
        image = nib.load(t1_path)
        t1 = image.get_fdata(dtype=np.float32).squeeze()
        synthetic = synth_t2(t1, seed=args.seed_offset + idx)

        subject_out = os.path.join(args.out_dir, subject_name)
        os.makedirs(subject_out, exist_ok=True)
        nib.save(nib.Nifti1Image(synthetic[..., None], image.affine, image.header), os.path.join(subject_out, "slice_syntht2.nii.gz"))

    print(f"Wrote {len(subjects)} synthetic T2 slices to {args.out_dir}")


if __name__ == "__main__":
    main()
