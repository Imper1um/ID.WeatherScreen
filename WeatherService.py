from collections import defaultdict
import logging
import os
import requests
from datetime import datetime, timedelta, timezone
import dateutil.parser


class WeatherService:
    def __init__(self, api_key: str, location: str, wuApiKey: str = None, stationId: str = None):
        self.api_key = api_key
        self.location = location
        self.WuApiKey = wuApiKey
        self.StationId = stationId
        self.ForecastUrl = "http://api.weatherapi.com/v1/forecast.json"
        self.CurrentUrl = "http://api.weatherapi.com/v1/current.json"
        self.AstroTimesUrl = "https://api.sunrise-sunset.org/json"
        self.StationUrl = "https://api.weather.com/v2/pws/observations/current"
        self.StationHistoryUrl = "https://api.weather.com/v2/pws/history/all"
        self.Log = logging.getLogger("WeatherService")
        self.EnableTrace = os.getenv("ENABLE_TRACE", "No") == "Yes"

    def GetCurrentData(self):
        return self.ParseCurrentData(self.QueryCurrentData())

    def GetForecastData(self):
        return self.ParseForecastData(self.QueryForecastData())

    def GetStationHistory(self):
        return self.ParseHistoryData(self.QueryHistoryData())

    def OverlayStationData(self, currentData):
        if self.WuApiKey is None or self.StationId is None:
            return currentData;

        StationData = self.QueryStationData()
        if not StationData or "observations" not in StationData:
            return currentData

        if (self.EnableTrace):
            self.Log.debug(F"OverlayStationData: {StationData}")
            self.Log.debug("----")

        Observations = StationData["observations"][0]
        Imperial = Observations.get("imperial", {})

        NewData = currentData.copy()
        try:
            updates = {
                "Source": "Station",
                "StationID": Observations.get("stationID"),
                "LastUpdate": datetime.now()
            }

            if "obsTimeLocal" in Observations:
                updates["ObservedTimeLocal"] = datetime.strptime(Observations["obsTimeLocal"], "%Y-%m-%d %H:%M:%S").astimezone()
            if "obsTimeUtc" in Observations:
                updates["ObservedTimeUtc"] = datetime.fromisoformat(Observations["obsTimeUtc"]).astimezone(timezone.utc)

            if "winddir" in Observations:
                updates["WindDirection"] = Observations["winddir"]

            if "windSpeed" in Imperial:
                updates["WindSpeedMPH"] = Imperial["windSpeed"]

            if "windGust" in Imperial:
                updates["GustMPH"] = Imperial["windGust"]

            if "humidity" in Observations:
                updates["Humidity"] = Observations["humidity"]

            if "temp" in Imperial:
                updates["CurrentTempF"] = Imperial["temp"]

            if "heatIndex" in Imperial:
                updates["HeatIndex"] = Imperial["heatIndex"]

            if "uv" in Observations:
                updates["UVIndex"] = Observations["uv"]

            if "pressure" in Imperial:
                updates["PressureMB"] = round(Imperial["pressure"] * 33.8639, 1)

            if "precipTotal" in Imperial:
                updates["RainInches"] = Imperial["precipTotal"]

            # Only add fields if they are explicitly present
            NewData.update(updates)

            return NewData
        except Exception as e:
            self.Log.error(f"Failed to overlay station data: {e}")
            return currentData

    def QueryStationData(self):
        if not self.WuApiKey or not self.StationId:
            self.Log.debug("WUnderground station data not configured.")
            return None

        params = {
            "apiKey": self.WuApiKey,
            "stationId": self.StationId,
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
        if not self.WuApiKey or not self.StationId:
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
                "apiKey": self.WuApiKey,
                "stationId": self.StationId,
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
                    if (self.EnableTrace):
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
                        if (self.EnableTrace):
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

                    if (self.EnableTrace):
                        for d in datesComplete.keys():
                            self.Log.debug(F"datesComplete ({date}): {d} = {datesComplete[d]}")
                        for d in thisComplete.keys():
                            self.Log.debug(F"thisComplete ({date}): {d} = {datesComplete[d]}")

            except requests.RequestException as e:
                self.Log.warn(f"Failed to fetch WUnderground station history data: {e}")
                continue
        
        if (self.EnableTrace):
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

    def QueryCurrentData(self):
        params = {
            "key": self.api_key,
            "q": self.location
        }
        response = requests.get(self.CurrentUrl, params=params)
        response.raise_for_status()
        return response.json()

    def QueryForecastData(self):
        params = {
            "key": self.api_key,
            "q": self.location,
            "days": 2,
            "aqi": "no",
            "alerts": "no"
        }
        response = requests.get(self.ForecastUrl, params=params)
        response.raise_for_status()
        return response.json()

    def QuerySunData(self, latitude: float, longitude: float, date: str = "today"):
        params = {
            "lat": latitude,
            "lng": longitude,
            "date": date,
            "formatted": 0
        }
        response = requests.get(self.AstroTimesUrl, params=params)
        response.raise_for_status()
        return response.json()

    def ParseHistoryData(self, data):
        if (self.EnableTrace):
            self.Log.debug(F"ParseHistoryData: {data}")
            self.Log.debug("----")

        history = []

        if not data or "observations" not in data:
            return history

        observations = data["observations"]
        for obs in observations:
            try:
                timestampLocal = datetime.strptime(obs["obsTimeLocal"], "%Y-%m-%d %H:%M:%S").astimezone()
                timestampUtc = dateutil.parser.isoparse(obs["obsTimeUtc"]).astimezone(timezone.utc)
                imperial = obs.get("imperial", {})

                entry = {
                    "Source": "Station",
                    "StationID": obs.get("stationID"),
                    "WindDirection": obs.get("winddirAvg"),
                    "WindSpeedMPH": imperial.get("windspeedAvg"),
                    "Humidity": obs.get("humidityAvg"),
                    "CurrentTempF": imperial.get("tempAvg"),
                    "HeatIndex": imperial.get("heatindexAvg"),
                    "UVIndex": obs.get("uvHigh", 0.0),
                    "PressureMB": None,
                    "RainInches": imperial.get("precipTotal", 0.0),
                    "CloudCover": None,
                    "GustMPH": imperial.get("windgustAvg"),
                    "VisibilityMiles": None,
                    "LastUpdate": datetime.utcnow(),
                    "ObservedTimeLocal": timestampLocal,
                    "ObservedTimeUtc": timestampUtc
                }

                history.append((timestampUtc, entry))

            except Exception as e:
                self.Log.warning(f"Failed to parse observation: {e}")
                continue

        return history


    def ParseCurrentData(self, data):
        if (self.EnableTrace):
            self.Log.debug(F"ParseCurrentData: {data}")
            self.Log.debug("----")
        current = data["current"];

        return {
            "Source": "WeatherAPI",
            "WindDirection": current["wind_degree"],
            "WindSpeedMPH": current["wind_mph"],
            "Humidity": current["humidity"],
            "CurrentTempF": current["temp_f"],
            "HeatIndex": current.get("feelslike_f", current["temp_f"]),
            "UVIndex": current["uv"],
            "State": current["condition"]["text"],
            "PressureMB": current["pressure_mb"],
            "RainInches": current["precip_in"],
            "CloudCover": current["cloud"],
            "GustMPH": current["gust_mph"],
            "VisibilityMiles": current["vis_miles"],
            "LastUpdate": datetime.now(),
            "ObservedTimeUtc": datetime.utcfromtimestamp(current["last_updated_epoch"]),
            "ObservedTimeLocal": datetime.fromtimestamp(current["last_updated_epoch"]).astimezone()
        }

    def ParseForecastData(self, data):
        if (self.EnableTrace):
            self.Log.debug(F"ParseForecastData: {data}")
            self.Log.debug("----")
        Latitude = data["location"]["lat"]
        Longitude = data["location"]["lon"]
        TodayDates = self.QuerySunData(Latitude, Longitude, "today")
        TomorrowDates = self.QuerySunData(Latitude, Longitude, "tomorrow")
        TodayForecast = data["forecast"]["forecastday"][0]
        TomorrowForecast = data["forecast"]["forecastday"][1]
        CurrentTime = data["current"]["last_updated_epoch"]
        LocalTime = datetime.fromtimestamp(CurrentTime)
        if LocalTime.hour >= 16:
            DayTimeForecast = TomorrowForecast
            DayTimeDates = TomorrowDates
        else:
            DayTimeForecast = TodayForecast
            DayTimeDates = TodayDates

        ForecastArray = TodayForecast["hour"] + TomorrowForecast["hour"]
        CurrentHourIndex = None

        for i, HourData in enumerate(ForecastArray):
            HourTime = datetime.strptime(HourData["time"], "%Y-%m-%d %H:%M")
            if HourTime.hour == LocalTime.hour and HourTime.date() == LocalTime.date():
                CurrentHourIndex = i
                break

        if CurrentHourIndex is None:
            raise ValueError("Couldn't find current hour in hourly data.")

        Next24HourForecast = ForecastArray[CurrentHourIndex:CurrentHourIndex + 24]
        BuildHours = []
        for hour in Next24HourForecast:
            BuildHours.append({
                "Time": hour["time"],
                "TemperatureF": hour["temp_f"],
                "RainChance": hour.get("chance_of_rain", 0),
                "CloudCoverPercentage": hour.get("cloud", 0),
                "WindDirection": hour["wind_degree"],
                "WindSpeedMPH": hour["wind_mph"],
                "WindGustMPH": hour.get("gust_mph", 0),
                "ConditionText": hour["condition"]["text"],
                "UVIndex": hour.get("uv", 0),
                "Humidity": hour.get("humidity", 0),
                "PrecipitationInches": hour.get("precip_in", 0.0),
                "PressureMB": hour.get("pressure_mb", 0.0),
            })

        


        return {
            "MoonPhase": TodayForecast["astro"]["moon_phase"],
            "Daytime": {
                "RainChance": DayTimeForecast["day"]["daily_chance_of_rain"],
                "PrecipitationInches": DayTimeForecast["day"]["totalprecip_in"],
                "HighF": DayTimeForecast["day"]["maxtemp_f"],
                "ForecastText": DayTimeForecast["day"]["condition"]["text"]
            },
            "Nighttime": {
                "RainChance": TodayForecast["day"]["totalprecip_in"],
                "LowF": TodayForecast["day"]["mintemp_f"],
                "ForecastText": TodayForecast["day"]["condition"]["text"]
            },
            "SunTimes": {
                "Today": {
                    "Sunrise": {
                        "AstronomicalTwilight": TodayDates["results"]["astronomical_twilight_begin"],
                        "NauticalTwilight": TodayDates["results"]["nautical_twilight_begin"],
                        "CivilTwilight": TodayDates["results"]["civil_twilight_begin"],
                        "Day": TodayDates["results"]["sunrise"],
                    },
                    "Sunset": {
                        "Start": TodayDates["results"]["sunset"],
                        "CivilTwilight": TodayDates["results"]["civil_twilight_end"],
                        "NauticalTwilight": TodayDates["results"]["nautical_twilight_end"],
                        "AstronomicalTwilight": TodayDates["results"]["astronomical_twilight_end"]
                    }
                },
                "Tomorrow": {
                    "Sunrise": {
                        "AstronomicalTwilight": TomorrowDates["results"]["astronomical_twilight_begin"],
                        "NauticalTwilight": TomorrowDates["results"]["nautical_twilight_begin"],
                        "CivilTwilight": TomorrowDates["results"]["civil_twilight_begin"],
                        "Day": TomorrowDates["results"]["sunrise"],
                    },
                    "Sunset": {
                        "Start": TomorrowDates["results"]["sunset"],
                        "CivilTwilight": TomorrowDates["results"]["civil_twilight_end"],
                        "NauticalTwilight": TomorrowDates["results"]["nautical_twilight_end"],
                        "AstronomicalTwilight": TomorrowDates["results"]["astronomical_twilight_end"]
                    }
                 }
            },
            "Next24Hours": BuildHours,
            "RainTimes": self.EstimateRainTimes(Next24HourForecast)
        }

    def EstimateRainTimes(self, forecast):
        RainStart = None
        RainEnd = None
        AlreadyRaining = False
        if forecast[0]["chance_of_rain"] > 30:
            AlreadyRaining = True

        for hour in forecast:
            time = hour["time"]
            will_rain = hour["chance_of_rain"] > 30
            if will_rain and not RainStart:
                RainStart = time
            if RainStart and not will_rain:
                RainEnd = time
                break
        return {"Start":RainStart, "End": RainEnd, "Already": AlreadyRaining}