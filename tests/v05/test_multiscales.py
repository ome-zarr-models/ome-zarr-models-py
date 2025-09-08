from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import numpy as np
import pytest
import zarr
from pydantic import ValidationError
from pydantic_zarr.v3 import AnyArraySpec, AnyGroupSpec, ArraySpec, GroupSpec

from ome_zarr_models.common.coordinate_transformations import (
    _build_transforms,
)
from ome_zarr_models.v05.axes import Axis
from ome_zarr_models.v05.coordinate_transformations import (
    VectorScale,
    VectorTranslation,
)
from ome_zarr_models.v05.image import Image
from ome_zarr_models.v05.multiscales import (
    Dataset,
    Multiscale,
)

if TYPE_CHECKING:
    from zarr.abc.store import Store

DEFAULT_UNITS_MAP = {"space": "meter", "time": "second"}


@pytest.fixture
def default_multiscale() -> Multiscale:
    """
    Return a valid Multiscale object.
    """
    axes = (
        Axis(name="c", type="channel", unit=None),
        Axis(name="z", type="space", unit="meter"),
        Axis(name="x", type="space", unit="meter"),
        Axis(name="y", type="space", unit="meter"),
    )
    rank = len(axes)
    transforms_top = _build_transforms(scale=(1,) * rank, translation=None)
    transforms_dset = _build_transforms(scale=(1,) * rank, translation=(0,) * rank)
    num_datasets = 3
    datasets = tuple(
        Dataset(path=f"path{idx}", coordinateTransformations=transforms_dset)
        for idx in range(num_datasets)
    )

    multi = Multiscale(
        axes=axes,
        datasets=datasets,
        coordinateTransformations=transforms_top,
    )
    return multi


def test_immutable(default_multiscale: Multiscale) -> None:
    """
    Check that models are immutable.
    """
    with pytest.raises(ValidationError, match="Instance is frozen"):
        default_multiscale.axes[0].name = "new_name"  # type: ignore[misc]


def test_multiscale_unique_axis_names() -> None:
    # TODO: is unique names actually part of the spec???
    axes = (
        Axis(name="x", type="space", unit="meter"),
        Axis(name="x", type="space", unit="meter"),
    )
    rank = len(axes)
    datasets = (Dataset.build(path="path", scale=(1,) * rank, translation=(0,) * rank),)

    with pytest.raises(ValidationError, match="Axis names must be unique."):
        Multiscale(
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(scale=(1, 1), translation=None),
        )


@pytest.mark.parametrize(
    "axis_types",
    [
        ("space", "space", "channel"),
    ],
)
def test_multiscale_space_axes_last(axis_types: list[str]) -> None:
    """
    Error if the last axes isn't 'space'.

    > ... the entries MUST be ordered by "type" where the
    > "time" axis must come first (if present), followed by the "channel" or
    > custom axis (if present) and the axes of type "space".
    """
    units_map = {"space": "meter", "time": "second"}
    axes = tuple(
        Axis(name=str(idx), type=t, unit=units_map.get(t))
        for idx, t in enumerate(axis_types)
    )
    rank = len(axes)
    datasets = (Dataset.build(path="path", scale=(1,) * rank, translation=(0,) * rank),)
    # TODO: make some axis-specific exceptions
    with pytest.raises(
        ValidationError, match="All space axes must be at the end of the axes list."
    ):
        Multiscale(
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(
                scale=(1,) * rank, translation=None
            ),
        )


@pytest.mark.parametrize(
    "axis_types",
    [
        ("channel", "time", "space", "space"),
    ],
)
def test_axes_order(axis_types: list[str]) -> None:
    """
    If 'time' is present, it must be first

    > ... the entries MUST be ordered by "type" where the
    > "time" axis must come first (if present), followed by the "channel" or
    > custom axis (if present) and the axes of type "space".
    """
    axes = tuple(
        Axis(name=str(idx), type=t, unit=DEFAULT_UNITS_MAP.get(t))
        for idx, t in enumerate(axis_types)
    )
    rank = len(axes)
    datasets = (Dataset.build(path="path", scale=(1,) * rank, translation=(0,) * rank),)
    with pytest.raises(
        ValidationError, match="Time axis must be at the beginning of axis list"
    ):
        Multiscale(
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(
                scale=(1,) * rank, translation=None
            ),
        )


@pytest.mark.parametrize("num_axes", [0, 1, 6, 7])
def test_multiscale_axis_length(num_axes: int) -> None:
    """
    > The length of "axes" must be between 2 and 5...
    """
    rank = num_axes
    axes = tuple(
        Axis(name=str(idx), type="space", unit="meter") for idx in range(num_axes)
    )
    datasets = (Dataset.build(path="path", scale=(1,) * rank, translation=(0,) * rank),)
    with pytest.raises(ValidationError, match=r"Length of axes \([0-9]+\) not valid"):
        Multiscale(
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(
                scale=(1,) * rank, translation=None
            ),
        )


def test_invalid_dataset_dimensions() -> None:
    """
    > Each "datasets" dictionary MUST have the same number of dimensions...
    """
    datasets = [
        Dataset.build(path="path", scale=(1,) * rank, translation=(0,) * rank)
        for rank in [2, 3]
    ]
    axes = tuple(Axis(name=str(idx), type="space", unit="meter") for idx in range(3))
    with pytest.raises(
        ValidationError,
        match=(
            "The length of axes does not match the dimensionality "
            "of the scale transform"
        ),
    ):
        Multiscale(
            axes=axes,
            datasets=datasets,
        )


@pytest.mark.parametrize(
    "scale, translation", [((1, 1), (1, 1, 1)), ((1, 1, 1), (1, 1))]
)
def test_transform_invalid_ndims(
    scale: tuple[int, ...], translation: tuple[int, ...]
) -> None:
    """
    Make sure dimensions of scale/translation transforms match.
    """
    with pytest.raises(
        ValidationError,
        match="The transforms have inconsistent dimensionality.",
    ):
        Dataset.build(path="foo", scale=scale, translation=translation)


@pytest.mark.parametrize(
    "transforms",
    [
        (
            VectorScale.build((1, 1, 1)),
            VectorTranslation.build((1, 1, 1)),
            VectorTranslation.build((1, 1, 1)),
        ),
        (VectorScale.build((1, 1, 1)),) * 5,
    ],
)
def test_transform_invalid_length(
    transforms: tuple[Any, ...],
) -> None:
    """
    Error if there's the wrong number of transforms.
    """
    with pytest.raises(
        ValidationError,
        match=re.escape(f"Length of transforms ({len(transforms)}) not valid"),
    ):
        Dataset(path="foo", coordinateTransformations=transforms)


@pytest.mark.parametrize(
    "transforms",
    [
        (VectorTranslation.build((1, 1, 1)),) * 2,
        (
            VectorTranslation.build((1, 1, 1)),
            VectorScale.build((1, 1, 1)),
        ),
    ],
)
def test_transform_invalid_first_element(
    transforms: tuple[Any, Any],
) -> None:
    """
    Make sure first transform element is a scale.
    """
    with pytest.raises(
        ValidationError,
        match="The first element of `coordinateTransformations` "
        "must be a scale transform",
    ):
        Dataset(path="foo", coordinateTransformations=transforms)


@pytest.mark.parametrize(
    "transforms",
    (
        (
            VectorScale.build((1, 1, 1)),
            VectorScale.build((1, 1, 1)),
        ),
    ),
)
def test_transform_invalid_second_element(
    transforms: tuple[VectorScale, VectorScale],
) -> None:
    """
    Make sure second transform is a translation.
    """
    with pytest.raises(
        ValidationError,
        match="The second element of `coordinateTransformations` "
        "must be a translation transform",
    ):
        Dataset(path="foo", coordinateTransformations=transforms)


def test_validate_axes_top_transforms() -> None:
    """
    Test that the number of axes must match the dimensionality of the
    top-level coordinateTransformations.
    """
    axes_rank = 3
    tforms_rank = 2
    msg_expect = (
        f"The length of axes does not match the dimensionality of "
        f"the scale transform in coordinateTransformations. "
        f"Got {axes_rank} axes, but the scale transform has "
        f"dimensionality {tforms_rank}"
    )
    with pytest.raises(
        ValidationError,
        match=msg_expect,
    ):
        Multiscale(
            name="foo",
            axes=[Axis(name=str(idx), type="space") for idx in range(axes_rank)],
            datasets=(
                Dataset.build(
                    path="foo", scale=(1,) * axes_rank, translation=(0,) * axes_rank
                ),
            ),
            coordinateTransformations=_build_transforms(
                scale=(1,) * tforms_rank, translation=None
            ),
        )


def test_validate_axes_dset_transforms() -> None:
    """
    Test that the number of axes must match the dimensionality of the
    per-dataset coordinateTransformations
    """
    axes_rank = 3
    tforms_rank = 2
    axes = [Axis(name=str(idx), type="space") for idx in range(axes_rank)]

    msg_expect = (
        f"The length of axes does not match the dimensionality of "
        f"the scale transform in datasets[0].coordinateTransformations. "
        f"Got {axes_rank} axes, but the scale transform has "
        f"dimensionality {tforms_rank}"
    )

    with pytest.raises(
        ValidationError,
        match=re.escape(msg_expect),
    ):
        Multiscale(
            name="foo",
            axes=axes,
            datasets=[
                Dataset.build(
                    path="foo", scale=(1,) * tforms_rank, translation=(0,) * tforms_rank
                )
            ],
            coordinateTransformations=_build_transforms(
                scale=(1,) * axes_rank, translation=None
            ),
        )


def test_ordered_multiscales() -> None:
    """
    > The "path"s MUST be ordered from largest (i.e. highest resolution) to smallest.
    """
    axes = (
        Axis(name="c", type="channel", unit=None),
        Axis(name="z", type="space", unit="meter"),
        Axis(name="x", type="space", unit="meter"),
        Axis(name="y", type="space", unit="meter"),
    )
    datasets = (
        Dataset(
            path="0",
            coordinateTransformations=(VectorScale(type="scale", scale=(2, 2, 2, 2)),),
        ),
        Dataset(
            path="1",
            coordinateTransformations=(VectorScale(type="scale", scale=(2, 2, 1, 2)),),
        ),
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Dataset 0 has a lower resolution (scales = [2.0, 2.0, 2.0, 2.0]) "
            "than dataset 1 (scales = [2.0, 2.0, 1.0, 2.0])"
        ),
    ):
        Multiscale(
            axes=axes,
            datasets=datasets,
        )


def test_multiscale_group_datasets_ndim() -> None:
    """
    Test that creating a Image with arrays with mismatched shapes raises
    an exception

    > The length of "axes" ... MUST be equal to the dimensionality of the zarr arrays
    > storing the image data
    """
    true_ndim = 2
    bad_ndim = 3
    match = (
        "Length of arrays (got len(array_specs)=3) must be the same as "
        "length of paths (got len(paths)=2)"
    )
    with pytest.raises(ValueError, match=re.escape(match)):
        Image.new(
            array_specs=[ArraySpec.from_array(np.arange(10)) for _ in range(bad_ndim)],
            paths=[str(i) for i in range(true_ndim)],
            axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
            scales=((1, 1), (2, 2)),
            translations=((0, 0), (0.5, 0.5)),
        )


def test_multiscale_group_missing_arrays() -> None:
    """
    Test that creating a multiscale group fails when an expected Zarr array is missing
    """
    arrays = (
        zarr.zeros((10, 10)),
        zarr.zeros((5, 5)),
    )
    array_names = ("s0", "s1")
    array_specs: list[AnyArraySpec] = [
        ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
    ]
    group_model = Image.new(
        array_specs=array_specs,
        axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
        paths=array_names,
        scales=((1, 1), (2, 2)),
        translations=((0, 0), (0.5, 0.5)),
    )
    # remove an array, then re-create the model
    assert group_model.members is not None
    group_model_broken = group_model.model_copy(
        update={"members": {array_names[0]: group_model.members[array_names[0]]}}
    )
    with pytest.raises(
        ValidationError,
        match=(
            "The multiscale metadata references an array that does not exist in this "
        ),
    ):
        Image(**group_model_broken.model_dump())


def test_multiscale_group_ectopic_group() -> None:
    """
    Test that creating a multiscale group fails when an expected Zarr array
    is actually a group
    """
    arrays = (
        zarr.zeros((10, 10)),
        zarr.zeros((5, 5)),
    )
    array_names = ("s0", "s1")
    group_model = Image.new(
        array_specs=[
            ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
        ],
        axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
        paths=array_names,
        scales=((1, 1), (2, 2)),
        translations=((0, 0), (0.5, 0.5)),
    )
    # remove an array, then re-create the model
    group_model_broken = group_model.model_copy(
        update={"members": {array_names[0]: GroupSpec()}}
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(f"The node at {array_names[0]} is a group, not an array."),
    ):
        Image(**group_model_broken.model_dump())


def test_from_zarr_missing_metadata(
    store: Store,
    request: pytest.FixtureRequest,
) -> None:
    group_model: AnyGroupSpec = GroupSpec(attributes={"ome": {}})
    group = group_model.to_zarr(store, path="test")
    # store_path = store.path if hasattr(store, "path") else ""
    match = "multiscales\n  Field required"
    with pytest.raises(ValidationError, match=match):
        Image.from_zarr(group)


def test_from_zarr_missing_array(store: Store) -> None:
    """
    Test that creating a multiscale Group fails when an expected Zarr array is missing
    or is a group instead of an array
    """
    arrays = np.zeros((10, 10)), np.zeros((5, 5))
    group_path = "broken"
    arrays_names = ("s0", "s1")
    group_model = Image.new(
        array_specs=[
            ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
        ],
        axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
        paths=arrays_names,
        scales=((1, 1), (2, 2)),
        translations=((0, 0), (0.5, 0.5)),
    )

    # make an untyped model, and remove an array before serializing
    removed_array_path = arrays_names[0]
    model_dict = group_model.model_dump(exclude={"members": {removed_array_path: True}})
    broken_group = GroupSpec(**model_dict).to_zarr(store=store, path=group_path)
    match = "Expected to find an array at s0, but no array was found there"
    with pytest.raises(ValueError, match=match):
        Image.from_zarr(broken_group)


def test_from_zarr_ectopic_group(store: Store) -> None:
    """
    Test that creating a multiscale Group fails when an expected Zarr array is missing
    or is a group instead of an array
    """
    arrays = np.zeros((10, 10)), np.zeros((5, 5))
    group_path = "broken"
    arrays_names = ("s0", "s1")
    group_model = Image.new(
        array_specs=[
            ArraySpec.from_array(a, dimension_names=["x", "y"]) for a in arrays
        ],
        axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
        paths=arrays_names,
        scales=((1, 1), (2, 2)),
        translations=((0, 0), (0.5, 0.5)),
    )

    # make an untyped model, and remove an array before serializing
    removed_array_path = arrays_names[0]
    model_dict = group_model.model_dump(exclude={"members": {removed_array_path: True}})
    broken_group = GroupSpec(**model_dict).to_zarr(store=store, path=group_path)

    # put a group where the array should be
    broken_group.create_group(removed_array_path)
    match = "Expected to find an array at s0, but a group was found there instead."
    with pytest.raises(ValueError, match=match):
        Image.from_zarr(broken_group)


@pytest.mark.skip
def test_hashable(default_multiscale: Multiscale) -> None:
    """
    Test that `Multiscale` can be hashed
    """
    assert set(default_multiscale) == set(default_multiscale)
