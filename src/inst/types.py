from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class InstException(Exception):
    """Base class for exceptions in this module."""


@dataclass
class Media:
    type: MediaType
    url: str


@dataclass
class Post:
    media_list: List[Media]
    caption: Optional[str]


@dataclass
class Story:
    media: Media
