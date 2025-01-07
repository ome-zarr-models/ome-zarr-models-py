# Contributing

Thank you for spending your time contributing to the `ome-zarr-models-py` project.
We welcome contributions from everyone, no matter how little or large they are!
Below are some different ways you can contribute.

## Suggesting new features

We're super open to helper functionality for working with OME-Zarr metadata using our package!
To suggest a new feature, please open a ticket on [our issue tracker](https://github.com/ome-zarr-models/ome-zarr-models-py).

## Reporting issues

If you think you've found an issue or bug with this package, please report it on [our issue tracker](https://github.com/ome-zarr-models/ome-zarr-models-py).

## Implementing OME-Zarr RFCs

The request for comment (RFC) process in the OME-Zarr spec allows major changes or additions to be proposed to the specification.
We encourage RFC authors to implement OME-Zarr RFCs in this package, as a mechanism to see what the RFC looks like in practice before it is merged.

For every OME-Zarr RFC we will open an issue.
If you would like to implement it, please comment on that issue (so we can avoid duplication of work).
Then submit the changes to `ome-zarr-models-py` required to implement the RFC as a PR, and mention the PR in a comment on the issue.

## Contributing code

### Setting up a development environment

We use [uv](https://docs.astral.sh/uv/) for development.
To install development dependencies, run `uv sync`.

### Building the docs

We use [mkdocs](https://www.mkdocs.org/) for documentation.
`mkdocs` is auomatically installed as part of the `uv` development environment.
Run `mkdocs serve`, and open up the URL that your terminal prints.
