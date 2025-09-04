# How to obtain the data

Use the following command to update the submodules in this repository:

```bash
git submodule update --init --recursive
```

## Data in `ngff-rfc5-coordinate-transformation-examples`

Submodule from the repo data https://github.com/bogovicj/ngff-rfc5-coordinate-transformation-examples. Note that both Zarr v2 and Zarr v3 examples are available. `conftest.py` is used to configure the paths to the one being used (initially only Zarr v2 is used for testing).

## Data in `from_specification`

The data in `from_specification` is the one [introduced in the PR](https://github.com/bogovicj/ngff/tree/coord-transforms/latest/examples) from @bogovicj. Note that we need to call pytest with `--ignore=tests/data/examples/v06/ngff/tests` to avoid the tests in that folder interfering with our tests. This option is included in `pyproject.toml`.
