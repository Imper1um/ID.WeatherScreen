class ElementStore:
    def __init__(self, wrapper):
        self.PrimaryElement = ""
        self.BackingElements = []
        self.IsDeleted = False
        self.Wrapper = wrapper

    def AddPrimaryElement(self, id:str):
        self.PrimaryElement = id

    def AddBackingElement(self, id: str):
        self.BackingElements.append(id);

    def UpdateText(self, text: str):
        self.Wrapper.UpdateText(self, text)

    def ChangeImage(self, path: str, width: int, height: int):
        self.Wrapper.ChangeImage(self, path, width, height)

    def MoveSingle(self, x:int, y:int):
        self.Wrapper.MoveSingle(self, x, y)

    def MoveDouble(self, x1: int, y1: int, x2: int, y2: int):
        self.Wrapper.MoveDouble(self, x1, y1, x2, y2)

    def ChangeBackgroundImage(self, path: str):
        self.Wrapper.ChangeBackgroundImage(self, path)

    def Delete(self):
        self.Wrapper.Delete(self)