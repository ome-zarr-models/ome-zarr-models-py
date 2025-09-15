import argparse
import sys

from ome_zarr_models import __version__, open_ome_zarr


def main() -> None:
    """Main entry point for the ome-zarr-models CLI."""
    parser = argparse.ArgumentParser(
        prog="ome-zarr-models",
        description="OME-Zarr Models CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ome-zarr-models version {__version__}",
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # validate sub-command
    validate_cmd = subparsers.add_parser("validate", help="Validate an OME-Zarr")
    validate_cmd.add_argument("path", type=str, help="Path to zarr to validate")

    # info sub-command
    info_cmd = subparsers.add_parser("info", help="Get information about an OME-Zarr")
    info_cmd.add_argument(
        "path", type=str, help="Path to zarr to get information about"
    )

    args = parser.parse_args()

    # Execute the appropriate command
    match args.command:
        case "validate":
            validate(args.path)
        case "info":
            info(args.path)
        case None:
            parser.print_help()
            sys.exit(1)


def validate(path: str) -> None:
    """Validate an OME-Zarr at the given path.

    Examples
    --------
    ```bash
    ome-zarr-models validate https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr
    ```
    """
    import zarr

    group = zarr.open_group(path, mode="r")
    try:
        open_ome_zarr(group)
    except Exception as e:
        print(f"{e}\n")
        print("❌ Invalid OME-Zarr")
        sys.exit(1)
    print("✅ Valid OME-Zarr")


def info(path: str) -> None:
    """Print information about an OME-Zarr at the given path.

    Examples
    --------
    ```bash
    ome-zarr-models info https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr
    ome-zarr-models info https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0062A/6001240_labels.zarr
    ome-zarr-models info https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0083/9822152.zarr
    ome-zarr-models info https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0010/76-45.ome.zarr
    ```
    """
    import zarr

    try:
        from rich import print
    except ImportError:
        from builtins import print

    group = zarr.open_group(path, mode="r")
    obj = open_ome_zarr(group)
    print(obj)


if __name__ == "__main__":
    main()
