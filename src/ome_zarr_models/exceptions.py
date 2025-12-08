"""
Custom exceptions and warnings used by `ome-zarr-models`
"""

class ValidationWarning(UserWarning):
    """
    Warning emitted for OME-Zarr data that can be interpreted
    by `ome-zarr-models`, but is not strictly compliant with the specification.
    """