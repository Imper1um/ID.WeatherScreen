from typing import Optional
from core.drawing.ElementStore import ElementStore

class HumiditySquareStore:
    def __init__(self):
        self.OutsideRect:Optional[ElementStore] = None
        self.FillRect:Optional[ElementStore] = None
        self.Emoji:Optional[ElementStore] = None
        self.Text:Optional[ElementStore] = None