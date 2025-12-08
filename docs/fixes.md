# Metadata fixing

ome-zarr-models will attempt to fix metadata that is not technically compliant with the OME-Zarr specification, but can still be unambiguously interpreted and made compliant.
In these cases a ValidationWarning will be emitted explaining the fix made.
This provides a useful interface for software packages and users to read metadata with mistakes, but still access it from ome-zarr-models with those mistakes corrected.

ome-zarr-models will always write specification-compliant metadata.
The `ome-zarr-models validate` command will always validate on invalid metadata, regardless of whether a fix is available or not.

If you have a suggestion for a fix we could add, please open an issue!

## Implemented fixes

- If the "version" field is not present in OME-Zarr 0.5 Plate metadata it is automatically set to `"0.5"`.
- If the order of transforms is incorrect in OME-Zarr 0.4 images, they are automatically swapped to be in the correct order.
