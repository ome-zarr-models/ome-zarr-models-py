from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Literal
    import numpy.typing as npt
    from zarr.storage import FSStore, MemoryStore, NestedDirectoryStore

import operator
from itertools import accumulate

import numpy as np
import pytest
from pydantic import ValidationError
from pydantic_zarr.v2 import ArraySpec, GroupSpec
from zarr.util import guess_chunks

from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.multiscales import (
    Dataset,
    Multiscale,
    MultiscaleGroupAttrs,
    Multiscale,
    MultiscaleGroup
)
from ome_zarr_models.v04.coordinate_transformations import (
    VectorScale,
    VectorTranslation,
    _build_transforms,
)

@pytest.fixture
def default_multiscale() -> Multiscale:
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
        Dataset(
            path=f"path{idx}",
            coordinateTransformations=transforms_dset
        )
        for idx in range(num_datasets)
    )

    multi = Multiscale(
        name="foo",
        axes=axes,
        datasets=datasets,
        coordinateTransformations=transforms_top,
    )
    return multi


def test_multiscale_unique_axis_names() -> None:
    # make axis names collide
    axes = (
        Axis(name="x", type="space", unit="meter"),
        Axis(name="x", type="space", unit="meter"),
    )
    rank = len(axes)
    datasets = (
        Dataset(
            path="path",
            coordinateTransformations=_build_transforms(
                scale = (1,) * rank,
                translation = (0,) * rank
            ),
        ),
    )

    with pytest.raises(ValidationError, match="Axis names must be unique."):
        Multiscale(
            name="foo",
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(scale=(1, 1), translation=None),
        )


@pytest.mark.parametrize(
    "axis_types",
    [
        ("space", "space", "channel"),
        ("space", "channel", "space", "channel"),
    ],
)
def test_multiscale_space_axes_last(axis_types: list[str | None]) -> None:
    units_map = {"space": "meter", "time": "second"}
    axes = tuple(
        Axis(name=str(idx), type=t, unit=units_map.get(t))
        for idx, t in enumerate(axis_types)
    )
    rank = len(axes)
    datasets = (
        Dataset(
            path="path",
            coordinateTransformations=_build_transforms(
                scale = (1,) * rank,
                translation = (0,) * rank
            ),
        ),
    )
    # TODO: make some axis-specifc exceptions
    with pytest.raises(ValidationError, match="Space axes must come last."):
        Multiscale(
            name="foo",
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(scale=(1,) * rank, translation=None)
            )


@pytest.mark.parametrize("num_axes", [0, 1, 6, 7])
def test_multiscale_axis_length(num_axes: int) -> None:
    rank = num_axes
    axes = tuple(
        Axis(name=str(idx), type="space", unit="meter") for idx in range(num_axes)
    )
    datasets = (
        Dataset(
            path="path",
            coordinateTransformations=_build_transforms(
                scale = (1,) * rank,
                translation = (0,) * rank
            ),
        ),
    )
    with pytest.raises(ValidationError, match="Incorrect number of axes provided"):
        Multiscale(
            name="foo",
            axes=axes,
            datasets=datasets,
            coordinateTransformations=_build_transforms(scale=(1,) * rank, translation=None))


@pytest.mark.parametrize(
    "scale, translation", [((1, 1), (1, 1, 1)), ((1, 1, 1), (1, 1))]
)
def test_transform_invalid_ndims(
    scale: tuple[int, ...], translation: tuple[int, ...]
) -> None:
    tforms = _build_transforms(
        scale=scale,
        translation=translation,
    )
    with pytest.raises(
        ValidationError,
        match="The transforms have inconsistent dimensionality.",
    ):
        Dataset(path="foo", coordinateTransformations=tforms)


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
    with pytest.raises(
        ValidationError, match=f"after validation, not {len(transforms)}"
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
    with pytest.raises(
        ValidationError,
        match="Input should be a valid dictionary or instance of VectorScale",
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
    with pytest.raises(
        ValidationError,
        match="Input should be a valid dictionary or instance of VectorTranslation",
    ):
        Dataset(path="foo", coordinateTransformations=transforms)

def test_transform_axes_length() -> None:
    with pytest.raises(
        ValidationError,
        match="The number of axes must match the dimensionality of the coordinateTransformations",
    ):
        rank = 3
        Multiscale(
            name="foo",
            axes=[Axis(name="a", type='space'), Axis(name='b', type='space')],
            datasets=(
                Dataset(path="foo", coordinateTransformations=_build_transforms(scale=(1, 1), translation=None)),),
            coordinateTransformations=_build_transforms(scale=(1,) * rank, translation=None)
            )



@pytest.mark.skip
def test_multiscale_group_datasets_exist(
    default_multiscale: Multiscale,
) -> None:
    group_attrs = MultiscaleGroupAttrs(multiscales=(default_multiscale,))
    good_items = {
        d.path: ArraySpec(
            shape=(1, 1, 1, 1),
            dtype="uint8",
            chunks=(1, 1, 1, 1),
        )
        for d in default_multiscale.datasets
    }
    MultiscaleGroup(attributes=group_attrs, members=good_items)

    bad_items = {
        d.path + "x": ArraySpec(
            shape=(1, 1, 1, 1),
            dtype="uint8",
            chunks=(1, 1, 1, 1),
        )
        for d in default_multiscale.datasets
    }

    with pytest.raises(
        ValidationError,
        match="array with that name was found in the hierarchy",
    ):
        MultiscaleGroup(attributes=group_attrs, members=bad_items)


@pytest.mark.skip
def test_multiscale_group_datasets_rank(default_multiscale: Multiscale) -> None:
    group_attrs = MultiscaleGroupAttrs(multiscales=(default_multiscale,))
    good_items = {
        d.path: ArraySpec(
            shape=(1, 1, 1, 1),
            dtype="uint8",
            chunks=(1, 1, 1, 1),
        )
        for d in default_multiscale.datasets
    }
    MultiscaleGroup(attributes=group_attrs, members=good_items)

    # arrays with varying rank
    bad_items = {
        d.path: ArraySpec(
            shape=(1,) * (idx + 1),
            dtype="uint8",
            chunks=(1,) * (idx + 1),
        )
        for idx, d in enumerate(default_multiscale.datasets)
    }
    match = "Transform dimensionality must match array dimensionality."
    with pytest.raises(ValidationError, match=match):
        MultiscaleGroup(attributes=group_attrs, members=bad_items)

    # arrays with rank that doesn't match the transform
    bad_items = {
        d.path: ArraySpec(shape=(1,), dtype="uint8", chunks=(1,))
        for d in default_multiscale.datasets
    }
    with pytest.raises(ValidationError, match=match):
        # arrays with rank that doesn't match the transform
        bad_items = {
            d.path: ArraySpec(shape=(1,), dtype="uint8", chunks=(1,))
            for d in default_multiscale.datasets
        }
        MultiscaleGroup(attributes=group_attrs, members=bad_items)


@pytest.mark.skip
@pytest.mark.parametrize("name", [None, "foo"])
@pytest.mark.parametrize("type", [None, "foo"])
@pytest.mark.parametrize("path_pattern", ["{0}", "s{0}", "foo/{0}"])
@pytest.mark.parametrize("metadata", [None, {"foo": 10}])
@pytest.mark.parametrize("ndim", [2, 3, 4, 5])
@pytest.mark.parametrize("chunks", ["auto", "tuple", "tuple-of-tuple"])
@pytest.mark.parametrize("order", ["auto", "C", "F"])
def test_from_arrays(
    name: str | None,
    type: str | None,
    path_pattern: str,
    metadata: dict[str, int] | None,
    ndim: int,
    chunks: Literal["auto", "tuple", "tuple-of-tuple"],
    order: Literal["auto", "C", "F"],
) -> None:
    arrays = tuple(np.arange(x**ndim).reshape((x,) * ndim) for x in [3, 2, 1])
    paths = tuple(path_pattern.format(idx) for idx in range(len(arrays)))
    scales = tuple((2**idx,) * ndim for idx in range(len(arrays)))
    translations = tuple(
        (t,) * ndim
        for t in accumulate(
            [(2 ** (idx - 1)) for idx in range(len(arrays))], operator.add
        )
    )

    all_axes = tuple(
        [
            Axis(
                name="x",
                type="space",
            ),
            Axis(name="y", type="space"),
            Axis(name="z", type="space"),
            Axis(name="t", type="time"),
            Axis(name="c", type="barf"),
        ]
    )
    # spatial axes have to come last
    if ndim in (2, 3):
        axes = all_axes[:ndim]
    else:
        axes = tuple([*all_axes[4:], *all_axes[:3]])
    chunks_arg: tuple[tuple[int, ...], ...] | tuple[int, ...] | Literal["auto"]
    if chunks == "auto":
        chunks_arg = chunks
        chunks_expected = (
            guess_chunks(arrays[0].shape, arrays[0].dtype.itemsize),
        ) * len(arrays)
    elif chunks == "tuple":
        chunks_arg = (2,) * ndim
        chunks_expected = (chunks_arg,) * len(arrays)
    elif chunks == "tuple-of-tuple":
        chunks_arg = tuple((idx,) * ndim for idx in range(1, len(arrays) + 1))
        chunks_expected = chunks_arg

    if order == "auto":
        order_expected = "C"
    else:
        order_expected = order

    group = MultiscaleGroup.from_arrays(
        paths=paths,
        axes=axes,
        arrays=arrays,
        scales=scales,
        translations=translations,
        name=name,
        type=type,
        metadata=metadata,
        chunks=chunks_arg,
        order=order,
    )

    group_flat = group.to_flat()

    assert group.attributes.multiscales[0].name == name
    assert group.attributes.multiscales[0].type == type
    assert group.attributes.multiscales[0].metadata == metadata
    assert group.attributes.multiscales[0].coordinateTransformations is None
    assert group.attributes.multiscales[0].axes == tuple(axes)
    for idx, array in enumerate(arrays):
        array_model: ArraySpec = group_flat["/" + paths[idx]]
        assert array_model.order == order_expected
        assert array.shape == array_model.shape
        assert array.dtype == array_model.dtype
        assert chunks_expected[idx] == array_model.chunks
        assert group.attributes.multiscales[0].datasets[
            idx
        ].coordinateTransformations == (
            VectorScale(scale=scales[idx]),
            VectorTranslation(translation=translations[idx]),
        )


@pytest.mark.skip
@pytest.mark.parametrize("name", [None, "foo"])
@pytest.mark.parametrize("type", [None, "foo"])
@pytest.mark.parametrize("dtype", ["uint8", np.uint8])
@pytest.mark.parametrize("path_pattern", ["{0}", "s{0}", "foo/{0}"])
@pytest.mark.parametrize("metadata", [None, {"foo": 10}])
@pytest.mark.parametrize("ndim", [2, 3, 4, 5])
@pytest.mark.parametrize("chunks", ["auto", "tuple", "tuple-of-tuple"])
@pytest.mark.parametrize("order", ["C", "F"])
def test_from_array_props(
    name: str | None,
    dtype: npt.DTypeLike,
    type: str | None,
    path_pattern: str,
    metadata: dict[str, int] | None,
    ndim: int,
    chunks: Literal["auto", "tuple", "tuple-of-tuple"],
    order: Literal["C", "F"],
) -> None:
    shapes = tuple((x,) * ndim for x in [3, 2, 1])
    dtype_normalized = np.dtype(dtype)
    paths = tuple(path_pattern.format(idx) for idx in range(len(shapes)))
    scales = tuple((2**idx,) * ndim for idx in range(len(shapes)))
    translations = tuple(
        (t,) * ndim
        for t in accumulate(
            [(2 ** (idx - 1)) for idx in range(len(shapes))], operator.add
        )
    )

    all_axes = tuple(
        [
            Axis(
                name="x",
                type="space",
            ),
            Axis(name="y", type="space"),
            Axis(name="z", type="space"),
            Axis(name="t", type="time"),
            Axis(name="c", type="barf"),
        ]
    )
    # spatial axes have to come last
    if ndim in (2, 3):
        axes = all_axes[:ndim]
    else:
        axes = tuple([*all_axes[4:], *all_axes[:3]])
    chunks_arg: tuple[tuple[int, ...], ...] | tuple[int, ...] | Literal["auto"]
    if chunks == "auto":
        chunks_arg = chunks
        chunks_expected = (guess_chunks(shapes[0], dtype_normalized.itemsize),) * len(
            shapes
        )
    elif chunks == "tuple":
        chunks_arg = (2,) * ndim
        chunks_expected = (chunks_arg,) * len(shapes)
    elif chunks == "tuple-of-tuple":
        chunks_arg = tuple((idx,) * ndim for idx in range(1, len(shapes) + 1))
        chunks_expected = chunks_arg

    order_expected = order

    group = MultiscaleGroup.from_array_props(
        dtype=dtype,
        shapes=shapes,
        paths=paths,
        axes=axes,
        scales=scales,
        translations=translations,
        name=name,
        type=type,
        metadata=metadata,
        chunks=chunks_arg,
        order=order,
    )

    group_flat = group.to_flat()

    assert group.attributes.multiscales[0].name == name
    assert group.attributes.multiscales[0].type == type
    assert group.attributes.multiscales[0].metadata == metadata
    assert group.attributes.multiscales[0].coordinateTransformations is None
    assert group.attributes.multiscales[0].axes == tuple(axes)
    for idx, shape in enumerate(shapes):
        array_model: ArraySpec = group_flat["/" + paths[idx]]
        assert array_model.order == order_expected
        assert shape == array_model.shape
        assert dtype_normalized == array_model.dtype
        assert chunks_expected[idx] == array_model.chunks
        assert group.attributes.multiscales[0].datasets[
            idx
        ].coordinateTransformations == (
            VectorScale(scale=scales[idx]),
            VectorTranslation(translation=translations[idx]),
        )


@pytest.mark.skip
@pytest.mark.parametrize(
    "store_type", ["memory_store", "fsstore_local", "nested_directory_store"]
)
def test_from_zarr_missing_metadata(
    store_type: Literal["memory_store", "fsstore_local", "nested_directory_store"],
    request: pytest.FixtureRequest,
) -> None:
    store: MemoryStore | NestedDirectoryStore | FSStore = request.getfixturevalue(
        store_type
    )
    group_model = GroupSpec()
    group = group_model.to_zarr(store, path="test")
    store_path = store.path if hasattr(store, "path") else ""
    match = (
        "Failed to find mandatory `multiscales` key in the attributes of the Zarr group at "
        f"{store}://{store_path}://{group.path}."
    )
    with pytest.raises(KeyError, match=match):
        MultiscaleGroup.from_zarr(group)


@pytest.mark.skip
@pytest.mark.parametrize(
    "store_type", ["memory_store", "fsstore_local", "nested_directory_store"]
)
def test_from_zarr_missing_array(
    store_type: Literal["memory_store", "fsstore_local", "nested_directory_store"],
    request: pytest.FixtureRequest,
) -> None:
    """
    Test that creating a multiscale Group fails when an expected Zarr array is missing
    or is a group instead of an array
    """
    store: MemoryStore | NestedDirectoryStore | FSStore = request.getfixturevalue(
        store_type
    )
    arrays = np.zeros((10, 10)), np.zeros((5, 5))
    group_path = "broken"
    arrays_names = ("s0", "s1")
    group_model = MultiscaleGroup.from_arrays(
        arrays=arrays,
        axes=(Axis(name="x", type="space"), Axis(name="y", type="space")),
        paths=arrays_names,
        scales=((1, 1), (2, 2)),
        translations=((0, 0), (0.5, 0.5)),
    )

    # make an untyped model, and remove an array before serializing
    removed_array_path = arrays_names[0]
    model_dict = group_model.model_dump(exclude={"members": {removed_array_path: True}})
    broken_group = GroupSpec(**model_dict).to_zarr(store=store, path=group_path)
    match = (
        f"Expected to find an array at {group_path}/{removed_array_path}, "
        "but no array was found there."
    )
    with pytest.raises(ValueError, match=match):
        MultiscaleGroup.from_zarr(broken_group)

    # put a group where the array should be
    broken_group.create_group(removed_array_path)
    match = (
        f"Expected to find an array at {group_path}/{removed_array_path}, "
        "but a group was found there instead."
    )
    with pytest.raises(ValueError, match=match):
        MultiscaleGroup.from_zarr(broken_group)


@pytest.mark.skip
def test_hashable(default_multiscale: Multiscale) -> None:
    """
    Test that `Multiscale` can be hashed
    """
    assert set(default_multiscale) == set(default_multiscale)