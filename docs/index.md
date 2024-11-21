# ome-zarr-models-py

This is a Python package that provides a Python object representation of an OME-zarr dataset.
It aims to be a reference implementation of the OME-zarr specification.

## Design

This package is designed with the following guiding principles:

- Strict adherence to the OME-zarr specification
- A usable set of Python classes for reading and writing and interacting with OME-zarr metadata
- A separate object for each version of the OME-zarr specification
- Data operations are out of scope

When adhering to the OME-zarr specification conflicts with usability, we choose adherence to the specification.
If you can think of an improvement to make this more usable that conflicts the specification, then we encourage you to suggest changes to the specifciation.
