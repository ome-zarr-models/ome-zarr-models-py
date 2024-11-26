# ome-zarr-models-py

This is a Python package that provides a Python object representation of an OME-zarr dataset.
It aims to be a reference implementation of the OME-zarr specification.

## Installing

Currently this package is only available in the GitHub repo.
Install it using:

```sh
pip install git+https://github.com/BioImageTools/ome-zarr-models-py.git@main
```

When we do a first release, it will be available on PyPI and conda-forge.

## Design

This package is designed with the following guiding principles:

- Strict adherence to the OME-zarr specification
- A usable set of Python classes for reading and writing and interacting with OME-zarr metadata
- A separate object for each version of the OME-zarr specification
- Array reading and writing operations are out of scope

We are trying to make this as usable and useful as possible while still complying with the OME-zarr specification.

## Roadmap

This is our draft roadmap.

### v1

- A working validator for OME-zarr 0.4 datasets

### v2

- Ability to write metadata after creation/modification
- A working validator for OME-zarr 0.5 datasets
