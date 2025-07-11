from typing import Optional
from core.drawing.ElementStore import ElementStore


class EmojiStore:
    def __init__(self, front:ElementStore = None, middle:ElementStore = None, back:ElementStore = None):
        self.Front: Optional[ElementStore] = front
        self.Middle: Optional[ElementStore] = middle
        self.Back: Optional[ElementStore] = back
        self.IsDeleted: bool = False

    def Delete(self):
        self.Front.Delete()
        self.Middle.Delete()
        self.Back.Delete()
        self.IsDeleted = True