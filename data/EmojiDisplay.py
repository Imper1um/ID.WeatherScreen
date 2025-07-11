from dataclasses import dataclass
from typing import Optional


@dataclass
class EmojiDisplay:
    Front: Optional[str] = None
    Middle: Optional[str] = None
    Back: Optional[str] = None