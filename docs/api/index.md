# API reference

This package contains a number of classes representing _OME-Zarr groups_.
Each of these classes represent a single OME-Zarr group.

Each group has a set of associated _metadata attributes_, which provide a listing of the OME-Zarr attributes available for each group.
To access these, use the `.ome_attributes` property on the group objects.

A listing of the group objects and associated metadata objects is given below for each version of the OME-Zarr specification.

## OME-Zarr 0.5

| OME-Zarr group objects                         | Metadata attributes                                                  | Creation helper                                      |
| ---------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------- |
| [`HCS`][ome_zarr_models.v05.HCS]               | [`HCSAttrs`][ome_zarr_models.v05.hcs.HCSAttrs]                       |
| [`Image`][ome_zarr_models.v05.Image]           | [`ImageAttrs`][ome_zarr_models.v05.image.ImageAttrs]                 | [`Image.new()`][ome_zarr_models.v05.image.Image.new] |
| [`Labels`][ome_zarr_models.v05.Labels]         | [`LabelsAttrs`][ome_zarr_models.v05.labels.LabelsAttrs]              |
| [`ImageLabel`][ome_zarr_models.v05.ImageLabel] | [`ImageLabelAttrs`][ome_zarr_models.v05.image_label.ImageLabelAttrs] |
| [`Well`][ome_zarr_models.v05.Well]             | [`WellAttrs`][ome_zarr_models.v05.well.WellAttrs]                    |

## OME-Zarr 0.4

| OME-Zarr group objects                         | Metadata attributes                                                  | Creation helper                                      |
| ---------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------- |
| [`HCS`][ome_zarr_models.v04.HCS]               | [`HCSAttrs`][ome_zarr_models.v04.hcs.HCSAttrs]                       |
| [`Image`][ome_zarr_models.v04.Image]           | [`ImageAttrs`][ome_zarr_models.v04.image.ImageAttrs]                 | [`Image.new()`][ome_zarr_models.v04.image.Image.new] |
| [`Labels`][ome_zarr_models.v04.Labels]         | [`LabelsAttrs`][ome_zarr_models.v04.labels.LabelsAttrs]              |
| [`ImageLabel`][ome_zarr_models.v04.ImageLabel] | [`ImageLabelAttrs`][ome_zarr_models.v04.image_label.ImageLabelAttrs] |
| [`Well`][ome_zarr_models.v04.Well]             | [`WellAttrs`][ome_zarr_models.v04.well.WellAttrs]                    |

## Helper functions

::: ome_zarr_models
