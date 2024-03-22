from pydantic import BaseModel
from typing import *


class Version(BaseModel):
    """
    Represents a software version with major, minor, and patch components.
    """
    major_version: Optional[int] = None
    minor_version: Optional[int] = None
    patch_version: Optional[int] = None


