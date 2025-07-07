from collections import defaultdict
from typing import List, Tuple

from core.WeatherEvent import WeatherEvent
from core.elements.ElementBase import ElementBase
from core.elements.ElementRefresh import ElementRefresh

from data import *

from core.store.WeatherDisplayStore import WeatherDisplayStore

from .WeatherScheduleItem import WeatherScheduleItem

class WeatherScheduler:
    def __init__(self, display):
        self.Display = display
        self.OnUpdateBackground = WeatherEvent(ElementRefresh.OnUpdateBackground)
        self.OnUpdateSunData = WeatherEvent(ElementRefresh.OnUpdateSunData)
        self.OnUpdateCurrentData = WeatherEvent(ElementRefresh.OnUpdateCurrentData)
        self.OnUpdateForecastData = WeatherEvent(ElementRefresh.OnUpdateForecastData)
        self.OnUpdateHistoryData = WeatherEvent(ElementRefresh.OnUpdateHistoryData)
        self.Timers:list[WeatherEvent] = []

    def UpdateTimers(self, timers:List[Tuple[ElementBase, ElementRefresh]]):
        timersByDelay = defaultdict(list)

        for (elementBase, elementRefresh) in timers:
            weatherScheduleItem = WeatherScheduleItem(elementRefresh, elementBase)
            for ev in elementRefresh.Reasons:
                if ev == ElementRefresh.OnUpdateBackground:
                    self.OnUpdateBackground.ActiveItems.append(weatherScheduleItem)
                elif ev == ElementRefresh.OnUpdateCurrentData:
                    self.OnUpdateCurrentData.ActiveItems.append(weatherScheduleItem)
                elif ev == ElementRefresh.OnUpdateForecastData:
                    self.OnUpdateForecastData.ActiveItems.append(weatherScheduleItem)
                elif ev == ElementRefresh.OnUpdateHistoryData:
                    self.OnUpdateHistoryData.ActiveItems.append(weatherScheduleItem)
                elif ev == ElementRefresh.OnUpdateSunData:
                    self.OnUpdateSunData.ActiveItems.append(weatherScheduleItem)
                elif ev == ElementRefresh.OnTimer:
                    timersByDelay[elementRefresh.Delay].append(weatherScheduleItem)

        for delay, items in timersByDelay.items():
            event = WeatherEvent(ElementRefresh.OnTimer, delay)
            event.ActiveItems.extend(items)
            self.Timers.append(event)
            self.Display.Root.after(delay, lambda ev=event: self._OnTimerFired(ev))
                

    def UpdateBackground(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData):
        i = self.OnUpdateBackground.OnEvent(store, forecast, current, history, sun)
        self.UpdateTimers(i)

    def UpdateCurrentData(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData):
        i = self.OnUpdateCurrentData.OnEvent(store, forecast, current, history, sun)
        self.UpdateTimers(i)
    
    def UpdateForecastData(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData):
        i = self.OnUpdateForecastData.OnEvent(store, forecast, current, history, sun)
        self.UpdateTimers(i)
    
    def UpdateHistoryData(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData):
        i = self.OnUpdateHistoryData.OnEvent(store, forecast, current, history, sun)
        self.UpdateTimers(i)
    
    def UpdateSunData(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData):
        i = self.OnUpdateSunData.OnEvent(store, forecast, current, history, sun)
        self.UpdateTimers(i)

    def _OnTimerFired(self, event: WeatherEvent):
        result = event.OnEvent(
            store=self.Display.WeatherDisplayStore,
            forecast=self.Display.ForecastData,
            current=self.Display.CurrentData,
            history=self.Display.HistoryData,
            sun=self.Display.SunData
        )
        self.UpdateTimers(result)

