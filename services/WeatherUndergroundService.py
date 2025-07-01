import dateutil, logging, requests

from collections import defaultdict
from datetime import datetime, timezone, timedelta

from config.WeatherConfig import WeatherConfig
from config.SettingsEnums import *

from data.CurrentData import CurrentData
from data.HistoryData import HistoryData, HistoryLine

def f_to_c(f:float) -> float: return (f - 32) * 5.0 / 9.0 if f is not None else None
def inhg_to_mb(hg:float) -> float: return hg * 33.8639 if hg is not None else None
def mph_to_kph(mph:float) -> float: return mph * 1.60934 if mph is not None else None
def miles_to_km(mi:int) -> int: return mi * 1.60934 if mi is not None else None
def in_to_mm(inch:float) -> float: return inch * 25.4 if inch is not None else None

class WeatherUndergroundService:
    def __init__(self, config: WeatherConfig):
        self.Log = logging.getLogger("WeatherUndergroundService")
        self.StationUrl = "https://api.weather.com/v2/pws/observations/current"
        self.StationHistoryUrl = "https://api.weather.com/v2/pws/history/all"
        self.Config = config

    def GetCurrentData(self) -> CurrentData:
        return self.ParseStationData(self.QueryStationData())

    def GetHistoryData(self) -> HistoryData:
        return self.ParseHistoryData(self.QueryHistoryData())

    def GetWind(self, wind: float) -> float:
        if (wind is None): return None
        if (self.Config.Weather.Wind == WindType.KPH):
            return mph_to_kph(wind)
        return wind;

    def GetTemperature(self, temp: float) -> float:
        if (temp is None): return None
        if (self.Config.Weather.Temperature == TemperatureType.C):
            return f_to_c(temp)
        return temp;

    def GetPressure(self, temp: float) -> float:
        if (temp is None): return None
        if (self.Config.Weather.Pressure == PressureType.HG):
            return inhg_to_mb(temp)
        return temp

    def GetPrecipitation(self, temp: float) -> float:
        if (temp is None): return None
        if (self.Config.Weather.Precipitation == PrecipitationType.MM):
            return in_to_mm(temp)
        return temp

    def GetDistance(self, distance: int) -> int:
        if (distance is None): return None
        if (self.Config.Weather.Visibility == VisibilityType.Kilometers):
            return miles_to_km(distance)
        return distance

    def ParseHistoryData(self, data) -> HistoryData:
        if self.Config.Logging.EnableTrace:
            self.Log.debug(f"ParseHistoryData: {data}")
            self.Log.debug("----")

        history = HistoryData()

        if not data or "observations" not in data:
            return history

        observations = data["observations"]
        for obs in observations:
            try:
                timestampLocal = datetime.strptime(obs["obsTimeLocal"], "%Y-%m-%d %H:%M:%S").astimezone()
                timestampUtc = dateutil.parser.isoparse(obs["obsTimeUtc"]).astimezone(timezone.utc)
                imperial = obs.get("imperial", {})

                wind = self.GetWind(imperial.get("windspeedAvg", 0.0))
                gust = self.GetWind(imperial.get("windgustAvg", 0.0))
                temp = self.GetTemperature(imperial.get("tempAvg", 32.0))
                dewpoint = self.GetTemperature(imperial.get("dewptAvg", 32.0))
                heatindex = self.GetTemperature(imperial.get("heatindexAvg", 32.0))
                pressure = self.GetPressure(imperial.get("pressureTrend", None))
                feelslike = self.GetTemperature(imperial.get("windchillAvg", 32.0))
                rain = self.GetPrecipitation(imperial.get("precipTotal", 0.0))

                entry = HistoryLine(
                    Source="Station",
                    StationId=obs.get("stationID"),
                    WindDirection=obs.get("winddirAvg"),
                    WindSpeed=wind,
                    WindGust=gust,
                    Humidity=obs.get("humidityAvg"),
                    CurrentTemp=temp,
                    FeelsLike=feelslike,
                    HeatIndex=heatindex,
                    DewPoint=dewpoint,
                    UVIndex=obs.get("uvHigh", 0.0),
                    Pressure=pressure,
                    Rain=rain,
                    LastUpdate=datetime.utcnow(),
                    ObservedTimeLocal=timestampLocal,
                    ObservedTimeUtc=timestampUtc
                )

                history.Lines.append(entry)

            except Exception as e:
                self.Log.warning(f"Failed to parse observation: {e}")
                continue
        return history

    def ParseStationData(self, data) -> CurrentData:
        if (not data or "observations" not in data):
            return None

        obs = data["observations"][0]
        imperial = obs.get("imperial", {})

        timestampLocal = datetime.strptime(obs["obsTimeLocal"], "%Y-%m-%d %H:%M:%S").astimezone()
        timestampUtc = dateutil.parser.isoparse(obs["obsTimeUtc"]).astimezone(timezone.utc)

        wind = self.GetWind(imperial.get("windSpeed", 0.0))
        gust = self.GetWind(imperial.get("windGust", 0.0))
        temp = self.GetTemperature(imperial.get("temp", 32.0))
        dewpoint = self.GetTemperature(imperial.get("dewpt", 32.0))
        heatindex = self.GetTemperature(imperial.get("heatIndex", 32.0))
        pressure = self.GetPressure(imperial.get("pressure", None))
        feelslike = self.GetTemperature(imperial.get("windChill", 32.0))
        rain = self.GetPrecipitation(imperial.get("precipTotal", 0.0))

        return CurrentData(
            Source="Station",
            Latitude=obs.get("lat"),
            Longitude=obs.get("lon"),
            StationId=obs.get("stationID"),
            WindDirection=obs.get("winddir"),
            WindSpeed=wind,
            WindGust=gust,
            Humidity=obs.get("humidity"),
            CurrentTemp=temp,
            FeelsLike=feelslike,
            HeatIndex=heatindex,
            DewPoint=dewpoint,
            UVIndex=obs.get("uv", 0.0),
            Pressure=pressure,
            Rain=rain,
            LastUpdate=datetime.utcnow(),
            ObservedTimeLocal=timestampLocal,
            ObservedTimeUtc=timestampUtc
        )

    def QueryStationData(self):
        if not self.Config.Services.WeatherUnderground.Key or not self.Config.Weather.StationCode:
            self.Log.debug("WUnderground station data not configured.")
            return None

        params = {
            "apiKey": self.Config.Services.WeatherUnderground.Key,
            "stationId": self.Config.Weather.StationCode,
            "format": "json",
            "units": "e",
            "numericPrecision": "decimal"
        }

        try:
            response = requests.get(self.StationUrl, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.Log.warn(f"Failed to fetch WUnderground station data: {e}")
            return None

    def QueryHistoryData(self):
        if not self.Config.Services.WeatherUnderground.Key or not self.Config.Weather.StationCode:
            self.Log.debug("WUnderground station data not configured.")
            return None

        now = datetime.now()
        nowUtc = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        nowHour = nowUtc.replace(minute=0,second=0,microsecond=0)
        self.Log.debug(F"QueryHistoryData: Querying {now} and {yesterday}...")

        observations = []
        datesComplete = defaultdict(int)

        for date in [yesterday, now]:
            params = {
                "apiKey": self.Config.Services.WeatherUnderground.Key,
                "stationId": self.Config.Weather.StationCode,
                "format": "json",
                "units": "e",
                "numericPrecision": "decimal",
                "date": date.strftime("%Y%m%d")
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
            }

            try:
                isDayDone = False
                tries = 0

                while (not isDayDone and tries < 3):
                    response = requests.get(self.StationHistoryUrl, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    tries += 1

                    lastHour = nowUtc - timedelta(hours=48)
                    self.Log.debug(F"{len(data['observations'])} records found for {date}")
                    if (self.Config.Logging.EnableTrace):
                        self.Log.debug(data)
                        self.Log.debug("----")

                    thisComplete = defaultdict(int)

                    for obs in data["observations"]:
                        hour = datetime.fromisoformat(obs["obsTimeUtc"]).replace(minute=0,second=0,microsecond=0,tzinfo=timezone.utc)
                        datesComplete[hour] = datesComplete[hour] + 1
                        thisComplete[hour] = thisComplete[hour] + 1
                        if (hour > lastHour):
                            lastHour = hour

                    if "observations" in data:
                        observations.extend(data["observations"])
                    if len(thisComplete.keys()) < 23 and not now == date:
                        self.Log.warn(F"Less than 23 hours were provided ({len(thisComplete.keys())} and it is not a today!) ")
                        if (self.Config.Logging.EnableTrace):
                            self.Log.debug(data)
                            self.Log.debug(params)
                    
                    isDayDone = True
                    for d in datesComplete.keys():
                        if d == nowHour:
                            continue
                        if d == lastHour:
                            continue
                        if datesComplete[d] < 10:
                            isDayDone = False
                            self.Log.warn(f"WUnderground only produced {datesComplete[d]} records for UTC {d}! Trying this day again.")

                    if (self.Config.Logging.EnableTrace):
                        for d in datesComplete.keys():
                            self.Log.debug(F"datesComplete ({date}): {d} = {datesComplete[d]}")
                        for d in thisComplete.keys():
                            self.Log.debug(F"thisComplete ({date}): {d} = {datesComplete[d]}")

            except requests.RequestException as e:
                self.Log.warn(f"Failed to fetch WUnderground station history data: {e}")
                continue
        
        if (self.Config.Logging.EnableTrace):
            for d in datesComplete.keys():
                self.Log.debug(F"datesComplete: {d} = {datesComplete[d]}")

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        expected_hours = {now - timedelta(hours=i) for i in range(24)}

        actual_hours = set()
        for obs in observations:
            try:
                hour = datetime.fromisoformat(obs["obsTimeUtc"]).replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                actual_hours.add(hour)
            except Exception as e:
                self.Log.warn(f"Failed to parse obsTimeUtc: {obs.get('obsTimeUtc')}, error: {e}")

        missing_hours = sorted(expected_hours - actual_hours)
        if missing_hours:
            self.Log.warn(f"Missing {len(missing_hours)} hourly observations in past 24 hours:")
            for hour in missing_hours:
                self.Log.warn(f"  - {hour.isoformat()}")

        return {"observations": observations} if observations else None
