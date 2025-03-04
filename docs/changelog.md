# Changelog

## 0.1.5

### New features

- Added a method to create new [ome_zarr_models.v04.Image][] objects from scratch.

### Minor improvements

- Improved the error message in [ome_zarr_models.open_ome_zarr][] when a Zarr group can't be validated with any OME-Zarr groups.
- Simplified the class inheritance structure across the package.

### Documentation improvements

- Added project governance to home page.

## 0.1.4

### Documentation improvements

- Added a versioning policy to the documentation home page.
- Added some missing objects to the API documentation for `ome_zarr_models.v04`.

## 0.1.3

### Documentation improvements

- General minor improvements to the layout and look of the API docs.
- Added some notes on known issues that will be encountered with support for OME-Zarr 0.5 in the future.

### New features

- The main OME-Zarr classes are now imported into the [ome_zarr_models.v04][] namespace, making them easier to import (e.g., what was `ome_zarr_models.v04.hcs.HCS` can now just be `ome_zarr_models.v04.HCS`).

## 0.1.2

### Documentation improvements

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

### Documentation improvements

- Fixed the `pip` install command on the home page.
- Added a conda install command to the home page.

## 0.1

First `ome-zarr-models` release.
