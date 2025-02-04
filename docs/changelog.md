# Changelog

## 0.1.2

### Doc improvements

- Added a ["How do I...?" page](how-to.md) that explains how to do common tasks with `ome-zarr-models`.

### New features

- Updated the return type on [ome_zarr_models.base.BaseGroup.ome_zarr_version] to allow "0.5" to be returned, in anticipation of upcoming support for OME-Zarr version 0.5.

### Bug fixes

- Added [ome_zarr_models.v04.image.Image][] to the `__all__` of [ome_zarr_models.v04.image][].
- Added [ome_zarr_models.v04.well.Well][] to the `__all__` of [ome_zarr_models.v04.well][].

## 0.1.1

### Bug fixes

- [ome_zarr_models.v04.image_label.ImageLabel][] data is now correctly parsed.
  Previously the `'image-label'` field was loaded, but not validated or parsed.

### Doc improvements

- Fixed the `pip` install command on the home page.
- Added a conda install command to the home page.

## 0.1

First `ome-zarr-models` release.
