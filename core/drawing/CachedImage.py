from PIL import ImageTk

class CachedImage:
    def __init__(self, path:str, img:ImageTk.PhotoImage, width:int, height: int):
        self.Path = path
        self.Image = img
        self.Width = width
        self.Height = height