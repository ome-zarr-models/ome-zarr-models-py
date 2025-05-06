# Dev Notes

Use the following command to update the submodules in this repository:
```bash
git submodule update --init --recursive
```

An extra step is required to enable sparse checkout for the `ngff` submodule 
(otherwise tests will fail because they will mix tests for `ome-zarr-models-py` and 
tests for `ngff`).

## Data in `ngff-rfc5-coordinate-transformation-examples`

Submodule from the repo data https://github.com/bogovicj/ngff-rfc5-coordinate-transformation-examples. Note that both Zarr v2 and Zarr v3 examples are available. `conftest.py` is used to configure the paths to the one being used.

## Data in `from_specification`

The data in `from_specification` is the one [introduced in the PR](https://github.com/bogovicj/ngff/tree/coord-transforms/latest/examples) from @bogovicj.

Using a submodule would add the whole repository, including the tests, and we want 
to avoid this.
The current approach is to use `git sparse-checkout`. This requires the following steps:

```
# Enable sparse checkout
git config core.sparseCheckout true

# Create or edit the sparse-checkout file and add the desired paths
INFO=".git/modules/tests/_rfc5_transforms/data_rfc5/ngff/info"
echo "0.6-dev/examples/coordSystems" > "$INFO"/sparse-checkout
echo "0.6-dev/examples/multiscales_strict" >> "$INFO"/sparse-checkout
echo "0.6-dev/examples/subspace" >> "$INFO"/sparse-checkout
echo "0.6-dev/examples/transformations" >> "$INFO"/sparse-checkout

# Navigate to the submodule directory
cd tests/_rfc5_transforms/data_rfc5/ngff

# Apply the sparse checkout configuration (i.e., filters the files to keep only the ones specified)
git read-tree -mu HEAD

# Verify that you only have the 0.6-dev folder
ls
```