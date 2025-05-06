# Dev notes

## Data in `from_specification`

The data in `from_specification` is the one [introduced in the PR](https://github.com/bogovicj/ngff/tree/coord-transforms/latest/examples) from @bogovicj.

Using a submodule would add the whole repository, so the current approach is to use 
`git sparse-checkout`. This requires the following steps:

```bash
# Enable sparse checkout for the submodule
git config -f .git/modules/tests/_rfc5_transforms/data_rfc5/ngff/config core.sparseCheckout true

# Navigate to the submodule directory
cd tests/_rfc5_transforms/data_rfc5/ngff

# Create or edit the sparse-checkout file and add the desired paths
echo "0.6-dev/examples/coordSystems" > .git/info/sparse-checkout
echo "0.6-dev/examples/multiscales_strict" >> .git/info/sparse-checkout
echo "0.6-dev/examples/subspace" >> .git/info/sparse-checkout
echo "0.6-dev/examples/transformations" >> .git/info/sparse-checkout

# Apply the sparse checkout configuration (i.e. filters the files to keep only the ones specified)
git read-tree -mu HEAD
```

## Data in `ngff-rfc5-coordinate-transformation-examples`

Submodule from the repo data https://github.com/bogovicj/ngff-rfc5-coordinate-transformation-examples. Note that both Zarr v2 and Zarr v3 examples are available. `conftest.py` is used to configure the paths to the one being used.
