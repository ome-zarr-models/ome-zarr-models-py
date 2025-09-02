# Changelog

## 1.0.0

### New Features

This is the first release to support OME-Zarr 0.5 🎉

### Updated dependencies

To support OME-Zarr 0.5, minimum dependencies have been updated to:

- `zarr` 3.1.1
- `pydantic` 2.11.5
- `pydantic-zarr` 0.8.2

### Breaking changes

- `ome_zarr_models.common.image_label_types.Label` has moved to [ome_zarr_models.v04.image_label_types.Label][].
- [ome_zarr_models.common.validation.check_array_path][] now takes a mandatory `expected_zarr_version` keyword-only argument.
- [ome_zarr_models.common.validation.check_group_spec][] and [ome_zarr_models.common.validation.check_array_spec][] raise a `ValueError` instead of a `RuntimeError`.

## 0.1.10

### Bug fixes

- Creating a `HCS` group with well paths that do not point to existing well Zarr groups
  no longer errors.

### Breaking changes

- `HCS.well_groups` will now only return well groups that exist, instead of erroring out if a well group is defined in the HCS metadata but does not exist as a Zarr group.

## 0.1.9

### Bug fixes

- Add a maximum `pydantic` requirement of version 2.11.4.
  This fixes issues using several classes in `ome-zarr-models`.
  We hope to fix and remove this `pydantic` pin in a new release shortly.

## 0.1.8

### Bug fixes

- Fixed serialising models with `model_dump(exclude_none=True)`.
  This (now fixed) bug was introduced in version 0.1.7.

## 0.1.7

### Bug fixes

- The `coordinateTransformations` field of multiscales metadata is no longer seralised if it is `None`.
  This fix is to stay compliant with the OME-Zarr specification, that does not explicitly allow `null` for this field.

## 0.1.6

### New features

- Added [ome_zarr_models.v04.Image.datasets][] as a convenience property to get all the datasests in an image.

### Minor improvements

- [ome_zarr_models.v04.Image.new][] now checks that `scales` and `translations` are both the same length as `paths`, and raises an error if they are not.

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
- Added some missing objects to the API documentation for v04.

## 0.1.3

### Documentation improvements

- General minor improvements to the layout and look of the API docs.
- Added some notes on known issues that will be encountered with support for OME-Zarr 0.5 in the future.

### New features

- The main OME-Zarr classes are now imported into the `ome_zarr_models.v04` namespace, making them easier to import (e.g., what was `ome_zarr_models.v04.hcs.HCS` can now just be `ome_zarr_models.v04.HCS`).

## 0.1.2

### Documentation improvements

- Added a ["How do I...?" page](how-to.md) that explains how to do common tasks with `ome-zarr-models`.

### New features

- Updated the return type on [ome_zarr_models.base.BaseGroup.ome_zarr_version] to allow "0.5" to be returned, in anticipation of upcoming support for OME-Zarr version 0.5.

### Bug fixes

- Added [ome_zarr_models.v04.image.Image][] to the `__all__` of `ome_zarr_models.v04.image`
- Added [ome_zarr_models.v04.well.Well][] to the `__all__` of `ome_zarr_models.v04.well`

## 0.1.1

### Bug fixes

- [ome_zarr_models.v04.image_label.ImageLabel][] data is now correctly parsed.
  Previously the `'image-label'` field was loaded, but not validated or parsed.

### Documentation improvements

- Fixed the `pip` install command on the home page.
- Added a conda install command to the home page.

## 0.1

First `ome-zarr-models` release.
