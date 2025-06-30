import logging
import requests

from datetime import datetime, timedelta
from CurrentData import CurrentData
from WeatherConfig import WeatherConfig
from WeatherAPIService import WeatherAPIService
from WeatherUndergroundService import WeatherUndergroundService
from SunriseSunsetService import SunriseSunsetService
from ForecastData import *
from HistoryData import HistoryData
from SunData import *

class WeatherService:
    def __init__(self, config: WeatherConfig):
        self.Log = logging.getLogger("WeatherService")
        self.Config = config
        self.WeatherAPIService = WeatherAPIService(config)
        self.WeatherUndergroundService = WeatherUndergroundService(config)
        self.SunriseSunsetService = SunriseSunsetService(config)
        

    def GetCurrentData(self) -> CurrentData:
        selections = self.Config.Services.Selections.Current
        if isinstance(selections, str):
            selections = [selections]

        combined_data = CurrentData()

        for source in selections:
            match source:
                case "WeatherAPI":
                    new_data = self.WeatherAPIService.GetCurrentData()
                case "WeatherUnderground":
                    new_data = self.WeatherUndergroundService.GetCurrentData()
                case _:
                    self.Log.warn(f"Unknown weather source: {source}")
                    continue

            if new_data:
                for field in new_data.__dataclass_fields__:
                    value = getattr(new_data, field)
                    if value is not None:
                        setattr(combined_data, field, value)

        if all(getattr(combined_data, field) is None for field in combined_data.__dataclass_fields__):
            self.Log.warn(f"No valid CurrentData sources returned any usable data from: {selections}")
            return None

        return combined_data

    def GetForecastData(self) -> ForecastData:
        match self.Config.Services.Selections.Forecast:
            case "WeatherAPI":
                return self.WeatherAPIService.GetForecastData()

        self.Log.warn(F"Current API Selection for ForecastData was {self.Config.Services.Selections.Forecast}, but that is not a valid data source for this operation.")
        return None

    def GetHistoryData(self) -> HistoryData:
        match self.Config.Services.Selections.History:
            case "WeatherUnderground":
                return self.WeatherUndergroundService.GetHistoryData()

        self.Log.warn(F"Current API Selection for HistoryData was {self.Config.Services.Seletions.History}, but that service is not configured.")
        return None

    def GetSunData(self, latitude, longitude, date: datetime) -> SunData:
        match self.Config.Services.Selections.Sun:
            case "SunriseSunset":
                return self.SunriseSunsetService.GetSunData(latitude, longitude, date)

        self.Log.warn(F"Current API Selection for SunData was {self.Config.Services.Selections.Sun}, but that service is not configured for this operation.")
        return None
    