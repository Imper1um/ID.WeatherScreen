from abc import ABC, abstractmethod
from core.elements.ElementRefresh import ElementRefresh
from core.store.WeatherDisplayStore import WeatherDisplayStore
from data import *

class ElementBase(ABC):
    @abstractmethod
    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        pass

    @abstractmethod
    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        pass