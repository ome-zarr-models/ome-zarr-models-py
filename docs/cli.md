# Command line interface

`ome-zarr-models` can validate and show metadata using a command line interface.

To see available commands,

```sh
ome-zarr-models --help
```

```
usage: ome-zarr-models [-h] [--version] COMMAND ...

OME-Zarr Models CLI

positional arguments:
  COMMAND     Available commands
    validate  Validate an OME-Zarr
    info      Get information about an OME-Zarr group

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

## Validation

To validate a OME-Zarr group, pass the path to the group to `ome-zarr-models validate`, for example

```sh
ome-zarr-models validate https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr
```

```
✅ Valid OME-Zarr
```

The group can be specified as any string that can be parsed by [zarr.open_group][].

## Info

To get information about an OME-Zarr group, pass the path to a group to `ome-zarr-models info`.
This will print the metadata (see below for an example).
If you have the [`rich`](https://rich.readthedocs.io) Python package installed, a more readable output will be produced.

```sh
ome-zarr-models info https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr
```

```
Image(
    zarr_format=3,
    node_type='group',
    attributes=BaseZarrAttrs[ImageAttrs](
        ome=ImageAttrs(
            version='0.5',
            multiscales=[
                Multiscale(
                    axes=[
                        Axis(name='y', type='space', unit='micrometer'),
                        Axis(name='x', type='space', unit='micrometer')
                    ],
                    datasets=(
                        Dataset(
                            path='0',
                            coordinateTransformations=(VectorScale(type='scale', scale=[1.6, 1.6]),)
                        ),
                        Dataset(
                            path='1',
                            coordinateTransformations=(VectorScale(type='scale', scale=[3.2, 3.2]),)
                        ),
                        Dataset(
                            path='2',
                            coordinateTransformations=(VectorScale(type='scale', scale=[6.4, 6.4]),)
                        ),
                        Dataset(
                            path='3',
                            coordinateTransformations=(VectorScale(type='scale', scale=[12.8, 12.8]),)
                        ),
                        Dataset(
                            path='4',
                            coordinateTransformations=(VectorScale(type='scale', scale=[25.6, 25.6]),)
                        ),
                        Dataset(
                            path='5',
                            coordinateTransformations=(VectorScale(type='scale', scale=[51.2, 51.2]),)
                        ),
                        Dataset(
                            path='6',
                            coordinateTransformations=(VectorScale(type='scale', scale=[102.4, 102.4]),)
                        ),
                        Dataset(
                            path='7',
                            coordinateTransformations=(VectorScale(type='scale', scale=[204.8, 204.8]),)
                        )
                    ),
                    coordinateTransformations=None,
                    metadata=None,
                    name='/',
                    type=None
                )
            ],
            _creator={'name': 'ome2024-ngff-challenge', 'version': '1.0.2', 'notes': None},
            omero={
                'channels': [
                    {
                        'active': True,
                        'coefficient': 1.0,
                        'color': 'FFFFFF',
                        'family': 'linear',
                        'inverted': False,
                        'label': 'Cy3',
                        'window': {'end': 55.0, 'max': 255.0, 'min': 0.0, 'start': 0.0}
                    }
                ],
                'id': 1,
                'rdefs': {'defaultT': 0, 'defaultZ': 0, 'model': 'greyscale'}
            }
        )
    ),
    members={
        '0': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085217.2919362,
                    'stop': 1729085219.378162,
                    'read': 29620797,
                    'written': 19813141,
                    'elapsed': 2.086225748062134,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(8978, 6510),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '1': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085219.4806092,
                    'stop': 1729085219.9208982,
                    'read': 7529704,
                    'written': 5313738,
                    'elapsed': 0.4402890205383301,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(4489, 3255),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '2': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085220.1890664,
                    'stop': 1729085220.455311,
                    'read': 1980204,
                    'written': 1412021,
                    'elapsed': 0.26624464988708496,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(2244, 1627),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '3': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085220.5030446,
                    'stop': 1729085220.6317737,
                    'read': 510798,
                    'written': 371051,
                    'elapsed': 0.12872910499572754,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(1122, 813),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '4': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085220.7549112,
                    'stop': 1729085220.8107944,
                    'read': 133911,
                    'written': 99335,
                    'elapsed': 0.055883169174194336,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(561, 406),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '5': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085220.852728,
                    'stop': 1729085220.8804672,
                    'read': 36408,
                    'written': 26760,
                    'elapsed': 0.027739286422729492,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(280, 203),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '6': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085220.9772055,
                    'stop': 1729085221.0321193,
                    'read': 9845,
                    'written': 7913,
                    'elapsed': 0.05491375923156738,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(140, 101),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        ),
        '7': ArraySpec(
            zarr_format=3,
            node_type='array',
            attributes={
                '_ome2024_ngff_challenge_stats': {
                    'input': '',
                    'output': '',
                    'start': 1729085221.1716456,
                    'stop': 1729085221.211354,
                    'read': 2677,
                    'written': 2953,
                    'elapsed': 0.03970837593078613,
                    'threads': 16,
                    'cpu_count': 16,
                    'sched_affinity': 16
                }
            },
            shape=(70, 50),
            data_type='uint8',
            chunk_grid={'name': 'regular', 'configuration': {'chunk_shape': (2048, 2048)}},
            chunk_key_encoding={'name': 'default', 'configuration': {'separator': '/'}},
            fill_value=0,
            codecs=(
                {
                    'name': 'sharding_indexed',
                    'configuration': {
                        'chunk_shape': (256, 256),
                        'codecs': (
                            {'name': 'bytes'},
                            {
                                'name': 'blosc',
                                'configuration': {
                                    'typesize': 1,
                                    'cname': 'zstd',
                                    'clevel': 5,
                                    'shuffle': 'bitshuffle',
                                    'blocksize': 0
                                }
                            }
                        ),
                        'index_codecs': (
                            {'name': 'bytes', 'configuration': {'endian': 'little'}},
                            {'name': 'crc32c'}
                        ),
                        'index_location': 'end'
                    }
                },
            ),
            storage_transformers=(),
            dimension_names=('y', 'x')
        )
    }
)
```
