"""OASIS 2D dataset loader for slice-based registration."""

import glob
import os

import nibabel as nib
import numpy as np
import torch
from torch.utils.data import Dataset


def load_nii_2d(path: str) -> np.ndarray:
    """Load a NIfTI slice and return a normalized float32 array."""
    arr = nib.load(path).get_fdata(dtype=np.float32).squeeze()
    mn, mx = arr.min(), arr.max()
    return (arr - mn) / (mx - mn + 1e-8)


def split_subjects(data_dir: str, split: str, val_ratio: float = 0.1, test_ratio: float = 0.1):
    """Return lexicographic subject split used by the OASIS loader."""
    all_subjects = sorted(glob.glob(os.path.join(data_dir, "OASIS_OAS1_*")))
    n = len(all_subjects)
    n_test = max(1, int(n * test_ratio))
    n_val = max(1, int(n * val_ratio))

    if split == "train":
        return all_subjects[: n - n_val - n_test]
    if split == "val":
        return all_subjects[n - n_val - n_test : n - n_test]
    if split == "test":
        return all_subjects[n - n_test :]
    raise ValueError(f"Unknown split: {split}")


class OASISDataset2D(Dataset):
    """OASIS 2D slice registration dataset.

    Expected directory structure:

        data/oasis/OASIS_OAS1_XXXX_MR1/
            slice_norm.nii.gz
            slice_seg24.nii.gz

    Each sample is a fixed/moving pair from different subjects.
    """

    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seg_key: str = "slice_seg24",
        max_train_pairs: int = 2000,
    ):
        super().__init__()
        self.seg_key = seg_key
        self.subjects = split_subjects(data_dir, split, val_ratio, test_ratio)

        subjects = self.subjects
        self.pairs = [
            (subjects[i], subjects[j])
            for i in range(len(subjects))
            for j in range(len(subjects))
            if i != j
        ]
        if split == "train" and len(self.pairs) > max_train_pairs:
            rng = np.random.default_rng(42)
            idx = rng.choice(len(self.pairs), max_train_pairs, replace=False)
            self.pairs = [self.pairs[k] for k in idx]

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> dict:
        fixed_subject, moving_subject = self.pairs[idx]

        fixed = torch.from_numpy(load_nii_2d(os.path.join(fixed_subject, "slice_norm.nii.gz"))).unsqueeze(0)
        moving = torch.from_numpy(load_nii_2d(os.path.join(moving_subject, "slice_norm.nii.gz"))).unsqueeze(0)

        sample = {"fixed": fixed, "moving": moving}

        fixed_seg_path = os.path.join(fixed_subject, f"{self.seg_key}.nii.gz")
        moving_seg_path = os.path.join(moving_subject, f"{self.seg_key}.nii.gz")
        if os.path.exists(fixed_seg_path) and os.path.exists(moving_seg_path):
            fixed_seg = nib.load(fixed_seg_path).get_fdata(dtype=np.float32).squeeze()
            moving_seg = nib.load(moving_seg_path).get_fdata(dtype=np.float32).squeeze()
            sample["fixed_seg"] = torch.from_numpy(fixed_seg).long()
            sample["moving_seg"] = torch.from_numpy(moving_seg).long()

        return sample
