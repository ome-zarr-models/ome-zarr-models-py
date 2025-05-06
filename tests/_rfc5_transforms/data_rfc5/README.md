# Dev notes

## Data in `from_specification`

The data in `from_specification` is the one [introduced in the PR](https://github.com/bogovicj/ngff/tree/coord-transforms/latest/examples) from @bogovicj.

This data is added via submodule using the sparse checkout git feature [guide on how to used it here](./sparse_checkout_guide.md).

## Data in `ngff-rfc5-coordinate-transformation-examples`

Submodule from the repo data https://github.com/bogovicj/ngff-rfc5-coordinate-transformation-examples. Note that both Zarr v2 and Zarr v3 examples are available. `conftest.py` is used to configure the paths to the one being used.
