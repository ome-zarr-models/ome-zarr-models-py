from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
import zarr
from zarr.storage import LocalStore

from ome_zarr_models._cli import main

from .conftest import Version, json_to_zarr_group

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path
    from typing import Any


def populate_fake_data(
    zarr_group: zarr.Group,
    default_dtype: str = "uint8",
) -> None:
    # Get the ome metadata from the group attributes
    # version 0.4 uses the root attributes, version 0.5 uses the "ome" attribute
    ome_attrs = cast("Mapping[str, Any]", zarr_group.attrs.get("ome", zarr_group.attrs))
    multiscales = ome_attrs.get("multiscales")
    if isinstance(multiscales, list):
        create_multiscales_data(zarr_group, multiscales, default_dtype)
        return

    # TODO?  could support fake data for other node types


def create_multiscales_data(
    zarr_group: zarr.Group,
    multiscales: Sequence[Mapping[str, Any]],
    default_dtype: str = "uint8",
) -> None:
    # Use the first multiscale (most common case)
    for multiscale in multiscales:
        if not (axes := multiscale.get("axes")):
            raise ValueError(
                f"No axes found in multiscale metadata from {zarr_group.store_path}"
            )
        if not (datasets := multiscale.get("datasets")):
            raise ValueError(
                f"No datasets found in multiscale metadata from {zarr_group.store_path}"
            )

        dimension_names = [axis["name"] for axis in axes]
        shape = (1,) * len(dimension_names)
        kwargs = {}
        if zarr_group.metadata.zarr_format >= 3:
            kwargs.update({"dimension_names": dimension_names})

        # Create arrays for each dataset path
        for dataset in datasets:
            if path := dataset.get("path"):
                zarr_group.create_array(
                    path,
                    shape=shape,
                    dtype=default_dtype,
                    **kwargs,  # type: ignore[arg-type]
                )


@pytest.mark.parametrize(
    "version,json_fname",
    [
        ("0.4", "multiscales_example.json"),
        ("0.5", "image_example.json"),
        ("0.5", "image_label_example.json"),
        ("0.5", "plate_example_1.json"),
    ],
)
@pytest.mark.parametrize("cmd", ["validate", "info"])
def test_cli_validate(
    version: Version,
    json_fname: str,
    cmd: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the CLI commands."""

    zarr_group = json_to_zarr_group(
        version=version, json_fname=json_fname, store=LocalStore(root=tmp_path)
    )
    populate_fake_data(zarr_group)
    monkeypatch.setattr("sys.argv", ["ome-zarr-models", cmd, str(tmp_path)])
    main()
    if cmd == "validate":
        assert "Valid OME-Zarr" in capsys.readouterr().out


@pytest.mark.parametrize("cmd", ["validate", "info"])
def test_cli_invalid(
    tmp_path: Path,
    cmd: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the CLI with no command."""
    zarr.create_group(tmp_path)
    monkeypatch.setattr("sys.argv", ["ome-zarr-models", cmd, str(tmp_path)])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
    assert "Invalid OME-Zarr" in capsys.readouterr().out
