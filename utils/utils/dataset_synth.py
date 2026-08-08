"""Synthetic T1-to-T2 contrast dataset derived from OASIS T1 slices."""

import glob
import os

import nibabel as nib
import numpy as np
import torch
from torch.utils.data import Dataset


BLACKLIST = {"OASIS_OAS1_0226_MR1"}


def synth_t2(t1: np.ndarray, seed: int = 0) -> np.ndarray:
    """Convert a normalized T1 slice in [0, 1] to a synthetic T2-like image."""
    rng = np.random.default_rng(seed)
    synthetic = 1.0 - np.power(t1.astype(np.float32), 0.7)
    synthetic += 0.15 * np.sin(np.pi * t1)
    synthetic += rng.normal(0.0, 0.015, size=t1.shape).astype(np.float32)
    lo, hi = synthetic.min(), synthetic.max()
    synthetic = (synthetic - lo) / (hi - lo + 1e-8)
    return synthetic.astype(np.float32)


def split_synth_subjects(oasis_dir: str, split: str, val_ratio: float = 0.1, test_ratio: float = 0.1):
    """Return deterministic train/validation/test subjects for synthetic pairs."""
    subjects = sorted(glob.glob(os.path.join(oasis_dir, "OASIS_OAS1_*")))
    subjects = [
        subject
        for subject in subjects
        if os.path.basename(subject) not in BLACKLIST
        and os.path.exists(os.path.join(subject, "slice_norm.nii.gz"))
    ]

    n = len(subjects)
    n_test = max(1, int(n * test_ratio))
    n_val = max(1, int(n * val_ratio))

    if split == "train":
        return subjects[: n - n_val - n_test]
    if split == "val":
        return subjects[n - n_val - n_test : n - n_test]
    if split == "test":
        return subjects[n - n_test :]
    raise ValueError(f"Unknown split: {split}")


class OASISSynthT2Dataset(Dataset):
    """OASIS-derived synthetic cross-modal registration dataset.

    Each sample returns a T1 fixed image and a synthetic T2-like moving image
    from the same subject. The ideal deformation is identity because both
    images share the same geometry.
    """

    def __init__(
        self,
        oasis_dir: str,
        split: str = "train",
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        noise_seed_offset: int = 1000,
    ):
        super().__init__()
        self.noise_seed_offset = noise_seed_offset
        self.subjects = split_synth_subjects(oasis_dir, split, val_ratio, test_ratio)

    def __len__(self) -> int:
        return len(self.subjects)

    def __getitem__(self, idx: int) -> dict:
        subject = self.subjects[idx]
        t1_path = os.path.join(subject, "slice_norm.nii.gz")
        t1_arr = nib.load(t1_path).get_fdata(dtype=np.float32).squeeze()

        fixed = torch.from_numpy(t1_arr).float().unsqueeze(0)
        moving = torch.from_numpy(synth_t2(t1_arr, seed=self.noise_seed_offset + idx)).float().unsqueeze(0)
        sample = {"fixed": fixed, "moving": moving}

        seg_path = os.path.join(subject, "slice_seg24.nii.gz")
        if os.path.exists(seg_path):
            seg_arr = nib.load(seg_path).get_fdata(dtype=np.float32).squeeze()
            sample["fixed_seg"] = torch.from_numpy(seg_arr).long()
            sample["moving_seg"] = sample["fixed_seg"].clone()

        return sample
