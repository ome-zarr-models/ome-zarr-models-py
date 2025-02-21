# Dev notes
The data in `from_specification` is the one [introduced in the PR](https://github.com/bogovicj/ngff/tree/coord-transforms/latest/examples) from @bogovicj.

This document keeps track of which data we are using for testing up to this point. The order below is the order in which we aim to implement the tests. On top of this data, we also have new test data.

Note: Some of the data from the specification needs fixes. Once the project is in the late stage, it will be important to diff the data with the one from the specification and make a PR to fix the issues in the NGFF specs.

## coordinate_systems
- [ ] arrayCoordSys.json

## transformations
- [x] identity.json
- [ ] scale.json
- [ ] translation.json
- [ ] sequence.json
- [ ] rotation.json
- [ ] affine2d2d.json
- [ ] affine2d3d.json
- [ ] mapAxis1.json
- [ ] mapAxis2.json
- [ ] byDimension1.json
- [ ] byDimension2.json
- [ ] byDimensionInvalid1.json
- [ ] byDimensionInvalid2.json
- [ ] displacementid.json
- [ ] inverseOf.json
- [ ] coordinates1d.json
- [ ] sequenceSubspace1.json
- [ ] bijection.json
- [ ] bijection_verbose.json
- [ ] xarrayLike.json
- [ ] byDimensionXarray.json
