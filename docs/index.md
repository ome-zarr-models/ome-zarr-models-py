# ome-zarr-models

A Python package for loading and validating OME-Zarr data.

The core of this package is a set of classes for representing different OME-Zarr groups:

| OME-Zarr 0.5                                   | OME-Zarr 0.4                                   |
| ---------------------------------------------- | ---------------------------------------------- |
| [`HCS`][ome_zarr_models.v05.HCS]               | [`HCS`][ome_zarr_models.v04.HCS]               |
| [`Image`][ome_zarr_models.v05.Image]           | [`Image`][ome_zarr_models.v04.Image]           |
| [`Labels`][ome_zarr_models.v05.Labels]         | [`Labels`][ome_zarr_models.v04.Labels]         |
| [`ImageLabel`][ome_zarr_models.v05.ImageLabel] | [`ImageLabel`][ome_zarr_models.v04.ImageLabel] |
| [`Well`][ome_zarr_models.v05.Well]             | [`Well`][ome_zarr_models.v04.Well]             |

Each class has

- a `.from_zarr()` method to read and validate groups
- easy access to all the OME-Zarr metadata
- a `.to_zarr()` method to write out metadata to Zarr groups.

## Installing

```sh
pip install ome-zarr-models
```

or

```sh
conda install -c conda-forge ome-zarr-models
```

## Getting started

- [The tutorial](tutorial.py) gives a worked example of using this package
- [How do I...?](how-to.md) explains how to do common tasks
- [The API reference](api/index.md) explains how this package is structured

## Design

This package has been designed with the following guiding principles:

- Strict adherence to the [OME-Zarr specification](https://ngff.openmicroscopy.org/), with the goal of being a reference implementation.
- A usable set of Python classes for reading, writing, and interacting with OME-Zarr metadata.
- The ability to work with multiple versions of the OME-Zarr spec at the same time.

Array reading and writing operations are out of scope, although the classes defined here make it easy to read array data from OME-Zarr groups.

## Getting help

Developers of this package are active on the [Zulip chat channel](https://imagesc.zulipchat.com/#narrow/channel/469152-ome-zarr-models-py), and happy to help.
Issues can also be opened on the [GitHub issue tracker](https://github.com/ome-zarr-models/ome-zarr-models-py/issues).

## zarr-python support

Versions 0.1.x of `ome-zarr-models` support `zarr-python` version 2 and OME-Zarr 0.4, and support will remain until the beginning of 2026.
Versions 1.x of `ome-zarr-models` require `zarr-python` version 3, and support versions of OME-Zarr >= 0.4.

## Known issues

- Because of the way this package is structured, it can't currently distinguish
  between values that are present but set to `null` in saved metadata, and
  fields that are not present.
- We do not currently validate [`bioformats2raw` metadata](https://ngff.openmicroscopy.org/0.4/index.html#bf2raw)
  This is because it is transitional, and we have decided to put time into implementing other
  parts of the specification. We would welcome a pull request to add this functionality though!

### OME-Zarr 0.5

- Since the first release of the OME-Zarr version 0.5 specification (commit [8a0f886](https://github.com/ome/ngff/tree/8a0f886aac791060e329874b624126d3530c2b6f)), the specification has been edited without the version number in OME-Zarr datasets being changed.
  As an implementation we have no way of knowing which version of the specification data that contains version "0.5" was written to, so **we have chosen to validate against the original release of OME-Zarr 0.5** (commit [8a0f886](https://github.com/ome/ngff/tree/8a0f886aac791060e329874b624126d3530c2b6f)).
  This means we do not:
  - Validate "omero" metadata.
- For labels, [the OME-Zarr specification says](https://ngff.openmicroscopy.org/0.5/index.html#labels-md) "Intermediate groups between "labels" and the images within it are allowed, but these MUST NOT contain metadata.". Because it is not clear what "metadata" means in this sentence, we do not validate this part of the specification.

## Versioning

`ome-zarr-models` has a major.minor versioning scheme where:

- The major version is incremented when support for a new version of the OME-Zarr specification is added, or a breaking change is made to the package.
- The minor version is incremented for any other changes (e.g., documentation improvements, bug fixes, new features)

Minor versions are released often with new improvements and bugfixes.

## Roadmap

- Support for open OME-Zarr RFCs.
- Emitting warnings when data violates "SHOULD" statements in the specification.

Is something missing from this list?
Or do you want to help implement our roadmap?
See [the contributing guide](contributing.md)!

## Governance

### Core maintainers

Core maintainers are the decision makers for the project, making decisions in consultation and consensus with the wider developer and user community.
They are also responsible for making releases of `ome-zarr-models`.
These are initially the founders of the project, and others can join by invitation after several sustained contributions to the project.
Core maintainers are expected to be active on maintaining the project, and should step down being core developers after a substantial period of inactivity.
For an up to date list, see the ["ome-zarr-models maintainers" team on GitHub](https://github.com/orgs/ome-zarr-models/teams/ome-zarr-models-maintainers).

### Core developers

Core developers have commit rights to the project, and are encouraged and trusted to use these to review and merge pull requests.
Anyone who has made a single contribution to the project will be invited to be a core developer.
For an up to date list, see the ["ome-zarr-models developers" team on GitHub](https://github.com/orgs/ome-zarr-models/teams/ome-zarr-models-developers).

### Reviewing and merging code

Code must be submitted via a pull request (PR), and any core developer (including the author of the PR) can merge the pull request using their judgment on whether it is ready to be merged or not.
Core developers are trusted to ask for review from other core developers on their own PRs when necessary.
