from dataclasses import dataclass, field

from config.TextElementSettings import TextElementSettings


@dataclass
class StackedEmojiElementSettings(TextElementSettings):
    Front: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=0, Anchor="center", Stroke=False))
    Middle: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=0, Anchor="center", Stroke=False))
    Back: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=0, Anchor="center", Stroke=False))