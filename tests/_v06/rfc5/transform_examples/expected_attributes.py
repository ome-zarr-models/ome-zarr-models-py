from collections import defaultdict
from pathlib import Path

from ome_zarr_models._v06.image import ImageAttrs

expected_attrs: dict[Path, None | ImageAttrs] = defaultdict(lambda: None)
