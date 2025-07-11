from dataclasses import dataclass
from typing import Optional

from config.IconType import IconType


@dataclass
class IconDisplay:
    Front: Optional[str] = None
    Middle: Optional[str] = None
    Icon: Optional[IconType] = None