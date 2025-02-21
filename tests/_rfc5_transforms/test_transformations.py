from ome_zarr_models._rfc5_transforms.coordinate_transformations import SpatialMapper, CoordinateSystem, CoordinateTransformation
from ome_zarr_models.common.axes import Axis
from tests._rfc5_transforms.conftest import read_in_json


def test_identity_transform():
    read = read_in_json(json_fname="identity.json", model_cls=SpatialMapper)
    in_memory = SpatialMapper(
        coordinateSystems=[
            CoordinateSystem(
                name='in',
                axes=[
                    Axis(name='j'),
                    Axis(name='i'),
                ]
            ),
            CoordinateSystem(
                name='out',
                axes=[
                    Axis(name='y'),
                    Axis(name='x'),
                ]
            ),
            CoordinateSystem(
                name='out2',
                axes=[
                    Axis(name='y'),
                    Axis(name='x'),
                ]
            ),
        ],
        coordinateTransformations=[
            CoordinateTransformation(type="identity", input="in", output="out")
        ]
    )
    assert read == in_memory


def test_transformation_inpout_output_validation():
    axis_names = ['a','b','c']
    cs_names = ["in","out","other"]
    axes = [Axis(name=i) for i in axis_names]
    csystems = [CoordinateSystem(name=i, axes=axes) for i in cs_names]
    failing_transformation = [CoordinateTransformation(type="identity", input="in", output="not_working")]
    working_transformation = [CoordinateTransformation(type="identity", input="in", output="out")]
    try:
        a=SpatialMapper(coordinateSystems=csystems, coordinateTransformations=failing_transformation)
    except Exception as e:
        print(f"Error: {e}")
    print()
