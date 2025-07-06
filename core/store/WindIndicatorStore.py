from typing import Optional
from core.drawing.ElementStore import ElementStore

class WindIndicatorStore:
    def __init__(self):
        self.Wind:Optional[ElementStore] = None
        self.Gust:Optional[ElementStore] = None
        self.Direction: Optional[ElementStore] = None
        self.PrimaryArrow: Optional[ElementStore] = None
        self.HistoryArrows: Optional[ElementStore] = None