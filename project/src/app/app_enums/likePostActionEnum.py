from enum import Enum


class LikePostActionEnum(str, Enum):
    """
    Defines the 'liking' action to perform
    """
    LIKE = "Like",
    UNLIKE = "Unlike"

