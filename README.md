# OASIS-SynthT2 Dataset Utilities

This repository provides neutral, reusable utilities for working with the public OASIS-1 / Learn2Reg OASIS brain MRI benchmark and for generating a synthetic T2-like contrast from normalized T1 slices.

It intentionally contains only public-data utility code and neutral documentation.

## What Is Included

- A download helper for the publicly available Learn2Reg OASIS data source.
- Lightweight PyTorch dataset loaders for:
  - OASIS 2D slice registration.
  - OASIS-derived synthetic T1-to-T2 contrast pairs.
- A script to materialize synthetic T2 slices from normalized T1 slices.
- A deterministic split description matching the dataset loader logic.

## What Is Not Included

- Original OASIS MRI files.
- Any restricted clinical data.
- Project-specific writing, figures, result tables, or research claims.
- Trained model checkpoints or private experiment logs.

Original OASIS / Learn2Reg data should be downloaded from the official public data source and used under the terms of the original data providers. The official Learn2Reg 2021 page describes Task 3 as an MR whole-brain registration dataset based on OASIS.

## Expected Data Layout

After downloading and preprocessing, place data under:

```text
data/oasis/
  OASIS_OAS1_0001_MR1/
    slice_norm.nii.gz
    slice_seg24.nii.gz
  OASIS_OAS1_0002_MR1/
    slice_norm.nii.gz
    slice_seg24.nii.gz
  ...
```

`slice_norm.nii.gz` is a normalized T1 slice. `slice_seg24.nii.gz` is an optional 24-structure segmentation label file used for anatomical evaluation.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the public Learn2Reg OASIS package:

```bash
python data/download_oasis.py --out_dir data/oasis_raw
```

Generate synthetic T2-like slices from prepared `slice_norm.nii.gz` files:

```bash
python scripts/create_syntht2.py --oasis_dir data/oasis --out_dir data/oasis_syntht2
```

Inspect deterministic train/validation/test splits:

```bash
python scripts/write_splits.py --oasis_dir data/oasis --out_dir metadata
```

## Synthetic T2 Mapping

For each normalized T1 slice `t1` in `[0, 1]`, the synthetic T2-like image is generated as:

```text
s = 1 - t1^0.7
s = s + 0.15 * sin(pi * t1)
s = s + Normal(0, 0.015)
s = normalize_to_0_1(s)
```

Noise is seeded deterministically from the subject index, making generated files reproducible.

## Split Policy

Subjects are sorted lexicographically. The default split is:

- Train: first 80%
- Validation: next 10%
- Test: final 10%

The synthetic loader excludes `OASIS_OAS1_0226_MR1` if present, matching the reproducible utility code in this repository.

## Citation

Please cite the original OASIS dataset publication when using OASIS data:

Marcus, D. S., Wang, T. H., Parker, J., Csernansky, J. G., Morris, J. C., & Buckner, R. L. (2007). Open Access Series of Imaging Studies (OASIS): Cross-sectional MRI data in young, middle aged, nondemented, and demented older adults. Journal of Cognitive Neuroscience, 19(9), 1498-1507. https://doi.org/10.1162/jocn.2007.19.9.1498

Also cite Learn2Reg if you use its preprocessed OASIS release.

## License

Code in this repository is released under the MIT License. Original OASIS / Learn2Reg data are not redistributed here and remain governed by their original terms.
