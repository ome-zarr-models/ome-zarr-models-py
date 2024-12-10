from ome_zarr_models.v04.image_label import Color, ImageLabelAttrs, Property, Source
from tests.v04.conftest import read_in_json


def test_image_label_example_json() -> None:
    model = read_in_json(
        json_fname="image_label_example.json", model_cls=ImageLabelAttrs
    )

    assert model == ImageLabelAttrs(
        colors=(
            Color(label_value=1, rgba=(255, 255, 255, 255)),
            Color(label_value=4, rgba=(0, 255, 255, 128)),
        ),
        properties=(
            Property(label_value=1, area=1200, cls="foo"),
            Property(label_value=4, area=1650),
        ),
        source=Source(image="../../"),
        version="0.4",
    )
