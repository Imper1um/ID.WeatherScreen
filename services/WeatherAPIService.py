import logging, requests
from datetime import datetime, timedelta

from config.IconType import IconType
from config.SettingsEnums import *
from config.WeatherConfig import WeatherConfig

from data.CurrentData import *
from data.ForecastData import *
from services.SunriseSunsetService import SunriseSunsetService

class WeatherAPIService:
    def __init__(self, config: WeatherConfig, sunriseSunsetService: SunriseSunsetService):
        self.Log = logging.getLogger("WeatherAPIService")
        self.Config = config
        self.CurrentUrl = "http://api.weatherapi.com/v1/current.json"
        self.ForecastUrl = "http://api.weatherapi.com/v1/forecast.json"
        self.AlertUrl = "http://api.weatherapi.com/v1/alerts.json"
        self.AstronomyUrl = "http://api.weatherapi.com/v1/astronomy.json"
        self.LastWeatherAPICurrentData = None
        self.LastWeatherAPIUpdate:Optional[datetime] = None
        self.SunriseSunsetService = sunriseSunsetService
        self.LastAlertUpdate: Optional[datetime] = None
        self.LastWeatherAPIAlerts = None
        self.LastAstronomyUpdate: Optional[datetime] = None
        self.LastAstronomyData = None
        

    def GetCurrentData(self):
        #Rate Limit = 15 minutes
        if (self.LastWeatherAPIUpdate is None or self.LastWeatherAPIUpdate + timedelta(minutes=15) > datetime.now()):
            self.LastWeatherAPIUpdate = datetime.now()
            self.LastWeatherAPICurrentData = self.ParseCurrentData(self.QueryCurrentData())
        return self.LastWeatherAPICurrentData

    def GetAstronomyData(self):
        if (self.LastAstronomyUpdate is None or self.LastAstronomyUpdate.date() != datetime.now().date()):
            self.LastAstronomyUpdate = datetime.now()
            self.LastAstronomyData = self.QueryAstronomyData()

        return self.LastAstronomyData

    def GetAlertData(self):
        if (self.LastAlertUpdate is None or self.LastAlertUpdate + timedelta(minutes=15) > datetime.now()):
            self.LastAlertUpdate = datetime.now()
            self.LastWeatherAPIAlerts = self.QueryAlertData()
        return self.LastWeatherAPIAlerts

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

    def QueryAstronomyData(self):
        params = {
            "key": self.Config.Services.WeatherAPI.Key,
            "q": self.Config.Weather.Location,
            "dt": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(self.AstronomyUrl, params=params)
        response.raise_for_status()
        return response.json()

    def QueryAlertData(self):
        params = {
            "key": self.Config.Services.WeatherAPI.Key,
            "q": self.Config.Weather.Location
        }
        response = requests.get(self.AlertUrl, params=params)
        response.raise_for_status()
        return response.json()

    def QueryForecastData(self):
        params = {
            "key": self.Config.Services.WeatherAPI.Key,
            "q": self.Config.Weather.Location,
            "days": 2,
            "aqi": "no",
            "alerts": "yes"
        }
        response = requests.get(self.ForecastUrl, params=params)
        response.raise_for_status()
        return response.json()

    
    def ParseCurrentData(self, data) -> CurrentData:
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"ParseCurrentData: {data}")
            self.Log.debug("----")
        current = data["current"];
        location = data["location"]
        observedUtc = datetime.utcfromtimestamp(current["last_updated_epoch"])
        observedLocal = datetime.fromtimestamp(current["last_updated_epoch"]).astimezone()

        temp = current["temp_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["temp_c"]
        feelsLike = current["feelslike_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["feelslike_c"]
        heatIndex = current["heatindex_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["heatindex_c"]
        dewpoint = current["dewpoint_f"] if self.Config.Weather.Temperature == TemperatureType.F else current["dewpoint_c"]
        pressure = current["pressure_mb"] if self.Config.Weather.Pressure == PressureType.MB else current["pressure_in"]
        rain = current["precip_in"] if self.Config.Weather.Precipitation == PrecipitationType.IN else current["precip_mm"]
        snow = current.get("snow_cm", 0.0) if self.Config.Weather.Precipitation == PrecipitationType.MM else current.get("snow_cm", 0.0) / 2.54
        visibility = current["vis_miles"] if self.Config.Weather.Visibility == VisibilityType.Miles else current["vis_km"]
        gust = current["gust_mph"] if self.Config.Weather.Wind == WindType.MPH else current["gust_kph"]
        wind = current["wind_mph"] if self.Config.Weather.Wind == WindType.MPH else current["wind_kph"]

        latitude = location["lat"]
        longitude = location["lon"]
        sunData = self.SunriseSunsetService.GetSunData(latitude, longitude, observedLocal)
        sunAngle = sunData.GetDegreesAboveHorizon(observedLocal)

        alerts = self.GetAlertData()
        astronomy = self.GetAstronomyData()

        moonPhase = None
        if (astronomy and astronomy.get("astronomy", None) and astronomy["astronomy"].get("astro", None) and astronomy["astronomy"]["astro"].get("moon_phase", None)):
            moonPhase = MoonPhase.FromString(astronomy["astronomy"]["astro"]["moon_phase"])

        hurricaneKeywords = ["hurricane", "tropical storm", "cyclone"]
        isHurricane = False
        if (alerts and alerts.get("alerts", None) and alerts["alerts"].get("alert", None)):
            for alert in alerts["alerts"]["alert"]:
                text = (alert.get("headline") or alert.get("event") or "").lower()
                if any(word in text for word in hurricaneKeywords):
                    isHurricane = True

        conditions = WeatherConditions(
            time=observedLocal,
            rainRate=rain,
            snowRate=snow,
            cloudCover=current["cloud"] / 100.0,
            moonPhase=moonPhase,
            windGust=gust,
            windSpeed=wind,
            visibility=visibility,
            sunAngle=sunAngle,
            isLightning="thunder" in current["condition"]["text"].lower(),
            isFoggy="fog" in current["condition"]["text"].lower(),
            isFreezing=temp <= 32,
            isHail="hail" in current["condition"]["text"].lower(),
            isWarning=False,
            isHurricane=isHurricane,
            stateConditions=current["condition"]["text"]
        )

        return CurrentData(
            Source="WeatherAPI",

            WindDirection=current["wind_degree"],
            Humidity=current["humidity"],
            CurrentTemp=temp,
            FeelsLike=feelsLike,
            HeatIndex=heatIndex,
            DewPoint=dewpoint,
            UVIndex=current["uv"],
            Pressure=pressure,
            LastUpdate=datetime.now(),
            ObservedTimeUtc=observedUtc,
            ObservedTimeLocal=observedLocal,
            Latitude=latitude,
            Longitude=longitude,

            Conditions=conditions
        )

    def ParseForecastData(self, data) -> ForecastData:
        if self.Config.Logging.EnableTrace:
            self.Log.debug(f"ParseForecastData: {data}")
            self.Log.debug("----")

        Latitude = data["location"]["lat"]
        Longitude = data["location"]["lon"]
        TodayForecast = data["forecast"]["forecastday"][0]
        TomorrowForecast = data["forecast"]["forecastday"][1]
        CurrentTime = data["current"]["last_updated_epoch"]
        LocalTime = datetime.fromtimestamp(CurrentTime)

        DayTimeForecast = TomorrowForecast if LocalTime.hour >= 16 else TodayForecast

        ForecastArray = TodayForecast["hour"] + TomorrowForecast["hour"]
        CurrentHourIndex = next(
            (i for i, h in enumerate(ForecastArray)
             if datetime.strptime(h["time"], "%Y-%m-%d %H:%M").hour == LocalTime.hour and
                datetime.strptime(h["time"], "%Y-%m-%d %H:%M").date() == LocalTime.date()),
            None
        )

        if CurrentHourIndex is None:
            raise ValueError("Couldn't find current hour in hourly data.")

        Next24HourForecast = ForecastArray[CurrentHourIndex:CurrentHourIndex + 24]
        astronomy = self.GetAstronomyData()
        moon_phase = MoonPhase.FromString(
            astronomy["astronomy"]["astro"]["moon_phase"]
        ) if astronomy and "astronomy" in astronomy and "astro" in astronomy["astronomy"] and "moon_phase" in astronomy["astronomy"]["astro"] else None

        hourly = []
        for hour in Next24HourForecast:
            hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
            sun_data = self.SunriseSunsetService.GetSunData(Latitude, Longitude, hour_time)
            sun_angle = sun_data.GetDegreesAboveHorizon(hour_time)
            condition_text = hour["condition"]["text"].lower()

            weather = WeatherConditions(
                time=hour_time,
                rainRate=hour.get("precip_in", 0.0),
                snowRate=hour.get("snow_cm", 0.0),
                cloudCover=hour.get("cloud", 0.0) / 100.0,
                moonPhase=moon_phase,
                windGust=hour.get("gust_mph", 0.0),
                windSpeed=hour.get("wind_mph", 0.0),
                visibility=hour.get("vis_miles", 0.0),
                sunAngle=sun_angle,
                isLightning="thunder" in condition_text,
                isFoggy="fog" in condition_text,
                isFreezing=hour.get("temp_f", 0.0) <= 32,
                isHail="hail" in condition_text,
                isWarning=False,
                isHurricane="hurricane" in condition_text,
                stateConditions=hour["condition"]["text"]
            )

            forecast = HourlyForecast(
                Time=hour["time"],
                Temperature=hour.get("temp_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("temp_c", 0.0),
                WindDirection=hour.get("wind_degree", 0),
                ConditionText=hour["condition"]["text"],
                UVIndex=hour.get("uv", 0.0),
                HeatIndex=hour.get("heatindex_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("heatindex_c", 0.0),
                FeelsLike=hour.get("feelslike_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("feelslike_c", 0.0),
                DewPoint=hour.get("dewpoint_f", 0.0) if self.Config.Weather.Temperature == TemperatureType.F else hour.get("dewpoint_c", 0.0),
                Pressure=hour.get("pressure_mb", 0.0) if self.Config.Weather.Pressure == PressureType.MB else hour.get("pressure_in", 0.0),
                Humidity=hour.get("humidity", 0),
                RainChance=hour.get("chance_of_rain", 0),
                SnowChance=hour.get("chance_of_snow", 0),
                Conditions=weather
            )

            hourly.append(forecast)

        return ForecastData(
            Moon=moon_phase,
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
            Next24Hours=hourly,
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