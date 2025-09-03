import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
    SequenceTransform,
    VectorScale,
    VectorTranslation,
)
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from tests._v06.conftest import (
    COORDINATE_SYSTEM_NAME_FOR_TESTS,
)


def test_ensure_scale_translation() -> None:
    def _gen_multiscale(
        coordinateTransformations: tuple[CoordinateTransformation, ...],
    ) -> Multiscale:
        extra_cs = CoordinateSystem(
            name=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            axes=[
                Axis(name="j"),
                Axis(name="i"),
            ],
        )
        return Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(extra_cs,),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=list(coordinateTransformations),
                ),
            ),
        )

    # ok (a single scale transformation)
    _ = _gen_multiscale(
        coordinateTransformations=(
            VectorScale(
                scale=[1.0, 1.0],
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (the first transformation should be a scale)
    with pytest.raises(
        ValidationError,
        match=(
            "The first transformation in `coordinateTransformations` must either "
            "be a `Scale` transform or a `Sequence`"
        ),
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                VectorTranslation(
                    translation=[1.0, 1.0],
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )

    # not ok (a tuple of > 1 transformation is not allowed, a sequence should be used
    # instead)
    with pytest.raises(
        ValidationError,
        match=r"Length of transforms \(2\) not valid. Allowed lengths are \[1\].",
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                VectorTranslation(
                    translation=[1.0, 1.0],
                    input="/0",
                    output="intermediate",  # can be anything, this case is not
                    # valid anyway
                ),
                VectorTranslation(
                    translation=[1.0, 1.0],
                    input="intermediate",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )

    # ok (a sequence of a scale and a translation)
    _ = _gen_multiscale(
        coordinateTransformations=(
            SequenceTransform(
                transformations=[
                    VectorScale(
                        scale=[1.0, 1.0],
                        input=None,
                        output=None,
                    ),
                    VectorTranslation(
                        translation=[1.0, 1.0],
                        input=None,
                        output=None,
                    ),
                ],
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (the scale and translations have different dimensionality)
    with pytest.raises(
        ValueError,
        match="The length of the scale and translation vectors must be the same",
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                SequenceTransform(
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                    transformations=[
                        VectorScale(scale=[1.0, 1.0], input=None, output=None),
                        VectorTranslation(
                            translation=[1.0, 1.0, 2.0], input=None, output=None
                        ),
                    ],
                ),
            )
        )


def test_invalid_dimensionalities() -> None:
    # not ok (one transformation has different dimensionality than the coordinate
    # system)
    with pytest.raises(
        ValidationError,
        match=(
            "All `Dataset` instances of a `Multiscale` must have the same "
            "dimensionality. Got "
        ),
    ):
        Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(
                CoordinateSystem(
                    name="out",
                    axes=[
                        Axis(name="j"),
                        Axis(name="i"),
                    ],
                ),
            ),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=[
                        VectorScale(
                            scale=[1.0, 1.0, 1.0],
                            input="/0",
                            output="out",
                        )
                    ],
                ),
                Dataset(
                    path="1",
                    coordinateTransformations=[
                        SequenceTransform(
                            transformations=[
                                VectorScale(
                                    scale=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                                VectorTranslation(
                                    translation=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                            ],
                            input="/1",
                            output="out",
                        )
                    ],
                ),
            ),
        )


def test_ensure_ordered_scales() -> None:
    with pytest.raises(
        ValidationError,
        match=r" has a lower resolution \(scales =",
    ):
        Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(
                CoordinateSystem(
                    name="out",
                    axes=[
                        Axis(name="j"),
                        Axis(name="i"),
                    ],
                ),
            ),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=[
                        VectorScale(
                            scale=[2.0, 2.0],
                            input="/0",
                            output="out",
                        )
                    ],
                ),
                Dataset(
                    path="1",
                    coordinateTransformations=[
                        SequenceTransform(
                            transformations=[
                                VectorScale(
                                    scale=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                                VectorTranslation(
                                    translation=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                            ],
                            input="/1",
                            output="out",
                        )
                    ],
                ),
            ),
        )

# TODO: all these tests have been copied over from v05, and needs to be adjusted
# def test_ordered_multiscales() -> None:
#     """
#     > The "path"s MUST be ordered from largest (i.e. highest resolution) to smallest.
#     """
#     axes = (
#         Axis(name="c", type="channel", unit=None),
#         Axis(name="z", type="space", unit="meter"),
#         Axis(name="x", type="space", unit="meter"),
#         Axis(name="y", type="space", unit="meter"),
#     )
#     datasets = (
#         Dataset(
#             path="0",
#             coordinateTransformations=(VectorScale(type="scale", scale=(2, 2, 2, 2)),),
#         ),
#         Dataset(
#             path="1",
#             coordinateTransformations=(VectorScale(type="scale", scale=(2, 2, 1, 2)),),
#         ),
#     )
#     with pytest.raises(
#         ValidationError,
#         match=re.escape(
#             "Dataset 0 has a lower resolution (scales = [2.0, 2.0, 2.0, 2.0]) "
#             "than dataset 1 (scales = [2.0, 2.0, 1.0, 2.0])"
#         ),
#     ):
#         Multiscale(
#             axes=axes,
#             datasets=datasets,
#         )
#
#
# def test_multiscale_group_datasets_ndim() -> None:
#     """
#     Test that creating a Image with arrays with mismatched shapes raises
#     an exception
#     > The length of "axes" ... MUST be equal to the dimensionality of the zarr arrays
#     > storing the image data
#     """
#     true_ndim = 2
#     bad_ndim = 3
#     match = (
#         "Length of arrays (got len(array_specs)=3) must be the same as "
#         "length of paths (got len(paths)=2)"
#     )
#     with pytest.raises(ValueError, match=re.escape(match)):
#         Image.new(
#             array_specs=[ArraySpec.from_array(np.arange(10)) for _ in range(bad_ndim)],
#             paths=[str(i) for i in range(true_ndim)],
#             axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
#             scales=((1, 1), (2, 2)),
#             translations=((0, 0), (0.5, 0.5)),
#         )
#
#
# def test_multiscale_group_missing_arrays() -> None:
#     """
#     Test that creating a multiscale group fails when an expected Zarr array is missing
#     """
#     arrays = (
#         zarr.zeros((10, 10)),
#         zarr.zeros((5, 5)),
#     )
#     array_names = ("s0", "s1")
#     array_specs: list[AnyArraySpec] = [
#         ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
#     ]
#     group_model = Image.new(
#         array_specs=array_specs,
#         axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
#         paths=array_names,
#         scales=((1, 1), (2, 2)),
#         translations=((0, 0), (0.5, 0.5)),
#     )
#     # remove an array, then re-create the model
#     assert group_model.members is not None
#     group_model_broken = group_model.model_copy(
#         update={"members": {array_names[0]: group_model.members[array_names[0]]}}
#     )
#     with pytest.raises(
#         ValidationError,
#         match=(
#             "The multiscale metadata references an array that does not exist in this "
#         ),
#     ):
#         Image(**group_model_broken.model_dump())
#
#
# def test_multiscale_group_ectopic_group() -> None:
#     """
#     Test that creating a multiscale group fails when an expected Zarr array
#     is actually a group
#     """
#     arrays = (
#         zarr.zeros((10, 10)),
#         zarr.zeros((5, 5)),
#     )
#     array_names = ("s0", "s1")
#     group_model = Image.new(
#         array_specs=[
#             ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
#         ],
#         axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
#         paths=array_names,
#         scales=((1, 1), (2, 2)),
#         translations=((0, 0), (0.5, 0.5)),
#     )
#     # remove an array, then re-create the model
#     group_model_broken = group_model.model_copy(
#         update={"members": {array_names[0]: GroupSpec()}}
#     )
#     with pytest.raises(
#         ValidationError,
#         match=re.escape(f"The node at {array_names[0]} is a group, not an array."),
#     ):
#         Image(**group_model_broken.model_dump())
#
#
# def test_from_zarr_missing_metadata(
#     store: Store,
#     request: pytest.FixtureRequest,
# ) -> None:
#     group_model: AnyGroupSpec = GroupSpec(attributes={"ome": {}})
#     group = group_model.to_zarr(store, path="test")
#     # store_path = store.path if hasattr(store, "path") else ""
#     match = "multiscales\n  Field required"
#     with pytest.raises(ValidationError, match=match):
#         Image.from_zarr(group)
#
#
# def test_from_zarr_missing_array(store: Store) -> None:
#     """
#     Test that creating a multiscale Group fails when an expected Zarr array is missing
#     or is a group instead of an array
#     """
#     arrays = np.zeros((10, 10)), np.zeros((5, 5))
#     group_path = "broken"
#     arrays_names = ("s0", "s1")
#     group_model = Image.new(
#         array_specs=[
#             ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
#         ],
#         axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
#         paths=arrays_names,
#         scales=((1, 1), (2, 2)),
#         translations=((0, 0), (0.5, 0.5)),
#     )
#
#     # make an untyped model, and remove an array before serializing
#     removed_array_path = arrays_names[0]
#     model_dict = group_model.model_dump(exclude={"members": {removed_array_path: True}})
#     broken_group = GroupSpec(**model_dict).to_zarr(store=store, path=group_path)
#     match = "Expected to find an array at broken/s0, but no array was found there"
#     with pytest.raises(ValueError, match=match):
#         Image.from_zarr(broken_group)
#
#
# def test_from_zarr_ectopic_group(store: Store) -> None:
#     """
#     Test that creating a multiscale Group fails when an expected Zarr array is missing
#     or is a group instead of an array
#     """
#     arrays = np.zeros((10, 10)), np.zeros((5, 5))
#     group_path = "broken"
#     arrays_names = ("s0", "s1")
#     group_model = Image.new(
#         array_specs=[
#             ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
#         ],
#         axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
#         paths=arrays_names,
#         scales=((1, 1), (2, 2)),
#         translations=((0, 0), (0.5, 0.5)),
#     )
#
#     # make an untyped model, and remove an array before serializing
#     removed_array_path = arrays_names[0]
#     model_dict = group_model.model_dump(exclude={"members": {removed_array_path: True}})
#     broken_group = GroupSpec(**model_dict).to_zarr(store=store, path=group_path)
#
#     # put a group where the array should be
#     broken_group.create_group(removed_array_path)
#     match = "Invalid value for 'node_type'. Expected 'array'. Got 'group"
#     with pytest.raises(ValueError, match=match):
#         Image.from_zarr(broken_group)
#
#
# @pytest.mark.skip
# def test_hashable(default_multiscale: Multiscale) -> None:
#     """
#     Test that `Multiscale` can be hashed
#     """
#     assert set(default_multiscale) == set(default_multiscale)