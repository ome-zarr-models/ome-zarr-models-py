import pytest

from ome_zarr_models.cli import main


@pytest.mark.parametrize(
    "url",
    [
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0062A/6001240_labels.zarr",
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0010/76-45.ome.zarr",
    ],
)
@pytest.mark.parametrize("cmd", ["validate", "info"])
def test_cli(url: str, cmd: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the CLI commands."""
    pytest.importorskip("zarr")
    aiohttp_exceptions = pytest.importorskip("aiohttp.client_exceptions")

    monkeypatch.setattr("sys.argv", ["ome-zarr-models", cmd, url])
    try:
        main()
    except aiohttp_exceptions.ClientConnectorError:
        pytest.xfail(reason="connection error")
