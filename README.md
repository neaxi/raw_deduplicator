# Mamuti PhotoRAW Deduplikator

## Purpose

When shooting photos in JPG+RAW combination, it's common to go through the JPGs during first filter wave as they render faster (smaller files, faster loading, ... ). RAW photos are moved to a subfolder (expected subfolder names: `raw`, `orf`).

In order to remove the RAW files corresponding to deleted JPGs, next step is to identify RAW photos matching the deleted JPGs and delete them too.

## Behavior

The script will consider files the "same", if the filename of JPG is the same as prefix of the RAW file (delimited by `-`). Extension is not considered either.

Example:

```sh
./demofolder
├── DSC0001.jpg             # JPGs kept after filtering
├── DSC0003.jpg
├── DSC0004.jpg
└── orf
    ├── DSC0001.orf         # kept, has matching JPG
    ├── DSC0002.orf         # deleted
    ├── DSC0003.orf         # kept
    ├── DSC0003-crop.orf    # kept, the name before "-" prefix matches
    └── DSC0004-HDR.dng     # kept, part before delimited matches, rest (incl. extension) is ignored
```
