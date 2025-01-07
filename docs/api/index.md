# API reference

This package contains a number of classes representing _OME-Zarr groups_.
Each of these classes represent at single OME-Zarr group.
To use them, load the zarr group first using `group = zarr.open_group(...)`, and then use `.from_zarr(group)` method on each of the OME-Zarr group objects in this package.

Each group has a set of associated _metadata attributes_, which provide a listing of the OME-Zarr attributes available for each group.
To access these, use the `.attributes` property on the group objects.

A listing of the group objects and associated metadata objects is given below for each version of the OME-Zarr specification.

## Top-level

::: ome_zarr_models

## v04

| OME-Zarr group objects                                     | Metadata attributes                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| [`HCS`][ome_zarr_models.v04.hcs.HCS]                       | [`HCSAttrs`][ome_zarr_models.v04.hcs.HCSAttrs]                       |
| [`Image`][ome_zarr_models.v04.image.Image]                 | [`ImageAttrs`][ome_zarr_models.v04.image.ImageAttrs]                 |
| [`Labels`][ome_zarr_models.v04.labels.Labels]              | [`LabelsAttrs`][ome_zarr_models.v04.labels.LabelsAttrs]              |
| [`ImageLabel`][ome_zarr_models.v04.image_label.ImageLabel] | [`ImageLabelAttrs`][ome_zarr_models.v04.image_label.ImageLabelAttrs] |
| [`Well`][ome_zarr_models.v04.well.Well]                    | [`WellAttrs`][ome_zarr_models.v04.well.WellAttrs]                    |

## Common objects

::: ome_zarr_models.base
