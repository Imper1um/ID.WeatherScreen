import logging
import requests
from datetime import datetime, timedelta
from CurrentData import *
from ForecastData import *
from WeatherConfig import *

class WeatherAPIService:
    def __init__(self, config: WeatherConfig):
        self.Log = logging.getLogger("WeatherAPIService")
        self.Config = config
        self.CurrentUrl = "http://api.weatherapi.com/v1/current.json"
        self.ForecastUrl = "http://api.weatherapi.com/v1/forecast.json"
        self.LastWeatherAPICurrentData = None
        self.LastWeatherAPIUpdate = None
        

    def GetCurrentData(self):
        #Rate Limit = 15 minutes
        if (self.LastWeatherAPIUpdate is None or self.LastWeatherAPIUpdate + timedelta(minutes=15) > datetime.now()):
            self.LastWeatherAPIUpdate = datetime.now()
            self.LastWeatherAPICurrentData = self.ParseCurrentData(self.QueryCurrentData())
        return self.LastWeatherAPICurrentData

    def GetForecastData(self):
        return self.ParseForecastData(self.QueryForecastData())

    def QueryCurrentData(self):
        params = {
            "key": self.Config.Services.WeatherAPI.Key,
            "q": self.Config.Weather.Location
        }
        response = requests.get(self.CurrentUrl, params=params)
        response.raise_for_status()
        return response.json()

    def QueryForecastData(self):
        params = {
            "key": self.Config.Services.WeatherAPI.Key,
            "q": self.Config.Weather.Location,
            "days": 2,
            "aqi": "no",
            "alerts": "no"
        }
        response = requests.get(self.ForecastUrl, params=params)
        response.raise_for_status()
        return response.json()
    
    def ParseCurrentData(self, data) -> CurrentData:
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"ParseCurrentData: {data}")
            self.Log.debug("----")
        current = data["current"];

        currentTemp = current["temp_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["temp_c"]
        pressure = current["pressure_mb"] if self.Config.Weather.Pressure == PressureType.MB else current["pressure_in"]
        rain = current["precip_in"] if self.Config.Weather.Precipitation == PrecipitationType.IN else current["precip_mm"]
        snow = current.get("snow_cm",0.0) if self.Config.Weather.Precipitation == PrecipitationType.MM else current.get("snow_cm",0.0) / 2.54
        feelsLike = current["feelslike_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["feelslike_c"]
        heatIndex = current["heatindex_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["heatindex_c"]
        dewpoint = current["dewpoint_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["dewpoint_c"]
        visibility = current["vis_miles"] if self.Config.Weather.Visibility == VisibilityType.Miles else current["vis_km"]
        gust = current["gust_mph"] if self.Config.Weather.Wind == WindType.MPH else current["gust_kph"]
        wind = current["wind_mph"] if self.Config.Weather.Wind == WindType.MPH else current["wind_kph"]

        return CurrentData(
            Source="WeatherAPI",
            Latitude=data["location"]["lat"],
            Longitude=data["location"]["lon"],
            WindDirection=current["wind_degree"],
            WindSpeed=wind,
            Humidity=current["humidity"],
            CurrentTemp=currentTemp,
            HeatIndex=heatIndex,
            FeelsLike=feelsLike,
            DewPoint=dewpoint,
            UVIndex=current["uv"],
            State=current["condition"]["text"],
            Pressure=pressure,
            Rain=rain,
            Snow=snow,
            CloudCover=current["cloud"],
            WindGust=gust,
            Visibility=visibility,
            LastUpdate=datetime.now(),
            ObservedTimeUtc=datetime.utcfromtimestamp(current["last_updated_epoch"]),
            ObservedTimeLocal=datetime.fromtimestamp(current["last_updated_epoch"]).astimezone()
        )

    def ParseForecastData(self, data) -> ForecastData:
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"ParseForecastData: {data}")
            self.Log.debug("----")
        Latitude = data["location"]["lat"]
        Longitude = data["location"]["lon"]
        TodayForecast = data["forecast"]["forecastday"][0]
        TomorrowForecast = data["forecast"]["forecastday"][1]
        CurrentTime = data["current"]["last_updated_epoch"]
        LocalTime = datetime.fromtimestamp(CurrentTime)
        if LocalTime.hour >= 16:
            DayTimeForecast = TomorrowForecast
        else:
            DayTimeForecast = TodayForecast

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

        return ForecastData(
            Moon=MoonPhase.FromString(TodayForecast["astro"]["moon_phase"]),
            Daytime=DaytimeData(
                RainChance=DayTimeForecast["day"]["daily_chance_of_rain"],
                SnowChance=DayTimeForecast["day"]["daily_chance_of_snow"],
                Rain=DayTimeForecast["day"]["totalprecip_in"] if self.Config.Weather.Precipitation == PrecipitationType.IN else DayTimeForecast["day"]["totalprecip_mm"],
                Snow=DayTimeForecast["day"]["totalsnow_cm"] if self.Config.Weather.Precipitation == PrecipitationType.MM else DayTimeForecast["day"]["totalsnow_cm"] / 2.54,
                High=DayTimeForecast["day"]["maxtemp_f"] if self.Config.Weather.Temperature == TemperatureType.F else DayTimeForecast["day"]["maxtemp_c"],
                ForecastText=DayTimeForecast["day"]["condition"]["text"]
            ),
            Nighttime=NighttimeData(
                Low=TodayForecast["day"]["mintemp_f"] if self.Config.Weather.Temperature == TemperatureType.F else TodayForecast["day"]["mintemp_c"],
                ForecastText=TodayForecast["day"]["condition"]["text"]
            ),
            Next24Hours=[HourlyForecast(
                Time=hour["time"],
                Temperature=hour.get("temp_f",0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("temp_c",0.0),
                CloudCoverPercentage=hour.get("cloud", 0),
                WindDirection=hour.get("wind_degree",0),
                WindSpeed=hour.get("wind_mph",0.0) if self.Config.Weather.Wind == WindType.MPH else hour.get("wind_kph",0.0),
                WindGust=hour.get("gust_mph", 0) if self.Config.Weather.Wind == WindType.KPH else hour.get("gust_kph", 0),
                ConditionText=hour["condition"]["text"],
                UVIndex=hour.get("uv", 0),
                HeatIndex=hour.get("heatindex_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("heatindex_c",0.0),
                FeelsLike=hour.get("feelslike_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("feelslike_c",0.0),
                DewPoint=hour.get("dewpoint_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("dewpoint_c",0.0),
                Pressure=hour.get("pressure_mb", 0.0) if self.Config.Weather.Pressure == PressureType.MB else hour.get("pressure_in", 0.0),
                Humidity=hour.get("humidity", 0),
                PrecipitationRain=hour.get("precip_in", 0.0) if self.Config.Weather.Precipitation == PrecipitationType.IN else hour.get("precip_mm",0.0),
                RainChance=hour.get("chance_of_rain", 0),
                PrecipitationSnow=hour.get("snow_cm", 0.0) if self.Config.Weather.Precipitation == PrecipitationType.MM else hour.get("snow_cm", 0.0) / 2.54,
                SnowChance=hour.get("chance_of_snow",0)
                
            ) for hour in Next24HourForecast],
            RainTimes=self.EstimateRainTimes(Next24HourForecast)
        )

    def EstimateRainTimes(self, forecast) -> RainTimesData:
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

        return RainTimesData(
            Start=RainStart,
            End=RainEnd,
            AlreadyRaining=AlreadyRaining
        )