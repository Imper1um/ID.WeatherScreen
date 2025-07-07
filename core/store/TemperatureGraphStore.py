from core.drawing.ElementStore import ElementStore


class TemperatureGraphStore:
    def __init__(self):
        self.ConnectingLines:list[ElementStore] = []
        self.Points:list[ElementStore] = []
        self.SmallTemps:list[ElementStore] = []
        self.TimeTemps:list[ElementStore] = []