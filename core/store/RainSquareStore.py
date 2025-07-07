from typing import Optional
from core.drawing.ElementStore import ElementStore

class RainSquareStore:
    def __init__(self):
        self.FillRect:Optional[ElementStore] = None
        self.OutsideRect:Optional[ElementStore] = None
        self.Emoji:Optional[ElementStore] = None
        self.Text:Optional[ElementStore] = None