from dataclasses import dataclass
from typing import Optional

from .TextElementSettings import TextElementSettings

@dataclass
class FormattedTextElementSettings(TextElementSettings):
    Format: Optional[str] = None