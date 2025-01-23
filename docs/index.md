# ome-zarr-models

A Python package that provides validation and a Pythonic interface for OME-Zarr datasets.

## Installing

```sh
pip install ome-zarr-models
```

or

```sh
conda install -c conda-forge ome-zarr-models
```

## Getting started

Useful places to get started are:

- [The tutorial](tutorial.py), which gives a worked example of using this package
- [The API reference](api/index.md), which explains how this package is structured

## Design

This package has been designed with the following guiding principles:

- Strict adherence to the [OME-Zarr specification](https://ngff.openmicroscopy.org/), with the goal of being a reference implementation.
- A usable set of Python classes for reading, writing, and interacting with OME-Zarr metadata.
- The ability to work with multiple versions of the OME-Zarr spec at the same time.
- Array reading and writing operations are out of scope.

## Getting help

Developers of this package are active on our [Zulip chat channel](https://imagesc.zulipchat.com/#narrow/channel/469152-ome-zarr-models-py), which is a great place for asking questions and getting help.

## Known issues

- Because of the way this package is structured, it can't currently distinguish
  between values that are present but set to `null` in saved metadata, and
  fields that are not present. Any fields set to `None` in the Python objects
  are currently not written when they are saved back to the JSON metadata using this package.
- We do not currently validate [`bioformats2raw` metadata](https://ngff.openmicroscopy.org/0.4/index.html#bf2raw)
  This is because it is transitional, and we have decided to put time into implementing other
  parts of the specification. We would welcome a pull request to add this functionality though!

## Roadmap

- Writing metadata after creation/modification.
- Support for OME-Zarr version 0.5.
- Emitting warnings when data violates "SHOULD" statements in the specification.
- Want to see a feature? See [the contributing guide](contributing.md)!
