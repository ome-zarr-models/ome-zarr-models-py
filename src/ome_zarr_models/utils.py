import pydantic
from dataclasses import MISSING, fields, is_dataclass
from pydantic import create_model

from typing import TypeVar
T = TypeVar("T")

def _unique_items_validator(values: list[T]) -> list[T]:
    for ind, value in enumerate(values, start=1):
        if value in values[ind:]:
            raise ValueError(f"Non-unique values in {values}.")
    return values

def dataclass_to_pydantic(dataclass_type: type) -> type[pydantic.BaseModel]:
    """Convert a dataclass to a Pydantic model.

    Parameters
    ----------
    dataclass_type : type
        The dataclass to convert to a Pydantic model.
    
    Returns
    -------
    type[pydantic.BaseModel] a Pydantic model class.
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"{dataclass_type} is not a dataclass")

    field_definitions = {}
    for _field in fields(dataclass_type):
        if _field.default is not MISSING:
            # Default value is provided
            field_definitions[_field.name] = (_field.type, _field.default)
        elif _field.default_factory is not MISSING:
            # Default factory is provided
            field_definitions[_field.name] = (_field.type, _field.default_factory())
        else:
            # No default value
            field_definitions[_field.name] = (_field.type, Ellipsis)

<<<<<<< HEAD
    return create_model(dataclass_type.__name__, **field_definitions)
=======
    return create_model(dataclass_type.__name__, **field_definitions)
>>>>>>> 470f4f1a33aef4ecf2ebf0906c912a3621c8957b
