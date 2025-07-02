from datetime import datetime

from config.SettingsEnums import TemperatureType
from .BaseHtmlBuilder import BaseHtmlBuilder
from core.WeatherDisplay import WeatherDisplay
from config.WeatherConfig import WeatherConfig

def MiddleContent(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
    tempAddon = "°F" if weatherConfig.Weather.Temperature == TemperatureType.F else "°C"
    weather = weatherDisplay.CurrentData.State
    time = datetime.now()
    timeDisplay = BaseHtmlBuilder.BuildLocalTime(time)
    timeData = BaseHtmlBuilder.BuildLocalDataTime(time)
    emoji = weatherDisplay.GetWeatherEmoji(weather, weatherDisplay.CurrentData.ObservedTimeLocal)

    hour = weatherDisplay.CurrentData.ObservedTimeLocal

    return BaseHtmlBuilder.MiddleContent(F"""
            {BaseHtmlBuilder.MiddleItem("localtime", "Local Time", timeDisplay, dataContent=timeData)}
            {BaseHtmlBuilder.MiddleItem("uptime", "Uptime", weatherDisplay.GetUptimeString())}
            {BaseHtmlBuilder.MiddleItem("temp", "Current Temp", F"{weatherDisplay.CurrentData.CurrentTemp:.0f}", tempAddon)}
            {BaseHtmlBuilder.MiddleItem("weather", "Weather", emoji['Emoji'])}
        """, classes="admin-middle-content")

class AdminHtmlBuilder:
    def Page(title: str, content: str, weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
        return BaseHtmlBuilder.Page(
            title=F"{title} - Admin",
            content="Your main admin content here",
            nav_title="WeatherScreen Admin",
            middleContent=MiddleContent(weatherDisplay, weatherConfig),
            nav_items=[
                ("Dashboard", "/"),
                ("Config", "/config"),
                ("Debug", "/debug"),
                ("Status", "/status")
            ]
        )
