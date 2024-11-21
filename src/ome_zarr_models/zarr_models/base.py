import pydantic

class FrozenBase(pydantic.BaseModel, frozen=True):
    """
    A frozen pydantic basemodel.
    """

