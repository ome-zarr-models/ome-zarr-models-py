import pydantic


class Base(pydantic.BaseModel):
    """
    The base pydantic model for all metadata classes
    """

    class Config:
        validate_assignment = True
