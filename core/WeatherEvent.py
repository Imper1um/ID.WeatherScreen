from typing import List, Tuple
from core.WeatherScheduleItem import WeatherScheduleItem
from core.elements import ElementBase
from core.elements.ElementRefresh import ElementRefresh
from core.store.WeatherDisplayStore import WeatherDisplayStore
from data import *


class WeatherEvent:
    def __init__(self, ev:str, delay:int = 0):
        self.Event = ev
        self.ActiveItems:list[WeatherScheduleItem] = []
        self.Delay = delay

    def OnEvent(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData) -> List[Tuple[ElementBase, ElementRefresh]]:
        results = []

        for i in self.ActiveItems[:]:
            if (i.IsSatisfied):
                self.ActiveItems.remove(i)
                continue
            r = i.Call(store, forecast, current, history, sun)
            results.append((i.ElementBase, r))
            self.ActiveItems.remove(i)

        return results
