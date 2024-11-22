import pydantic


class Base(pydantic.BaseModel):
    """
    The base pydantic model for all metadata classes
    """

    class Config:
        """
        Pydantic config.
        """

        validate_assignment = True
        extra = "allow"
