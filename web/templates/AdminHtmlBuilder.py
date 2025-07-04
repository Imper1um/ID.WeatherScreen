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
    timeData = [{ "key":"time","content":BaseHtmlBuilder.BuildLocalDataTime(time)},{"key":"item", "content":"localtime"}]
    emoji = weatherDisplay.GetWeatherEmoji(weather, weatherDisplay.CurrentData.ObservedTimeLocal)
    uptimeData = [{"key":"seconds","content":weatherDisplay.GetUptimeSeconds()},{"key":"item","content":"uptime"}]

    hour = weatherDisplay.CurrentData.ObservedTimeLocal

    return BaseHtmlBuilder.MiddleContent(F"""
            {BaseHtmlBuilder.MiddleItem("localtime", "Local Time", timeDisplay, dataContent=timeData, dataClasses="timeup data-item")}
            {BaseHtmlBuilder.MiddleItem("uptime", "Uptime", weatherDisplay.GetUptimeString(), dataContent=uptimeData, dataClasses="tickup data-item")}
            {BaseHtmlBuilder.MiddleItem("temp", "Current Temp", F"{weatherDisplay.CurrentData.CurrentTemp:.0f}", dataContent=[{"key":"item","content":"current-temp"}], addon=tempAddon, dataClasses="data-item")}
            {BaseHtmlBuilder.MiddleItem("weather", "Weather", emoji['Emoji'], dataContent=[{"key":"item","content":"current-emoji"}])}
        """, classes="admin-middle-content")

class AdminHtmlBuilder:
    def Page(title: str, content: str, weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
        return BaseHtmlBuilder.Page(
            title=F"{title} - Admin",
            content=content,
            nav_title="WeatherScreen Admin",
            middleContent=MiddleContent(weatherDisplay, weatherConfig),
            nav_items=[
                ("Dashboard", "/"),
                ("Config", "/config"),
                ("Debug", "/debug"),
                ("Status", "/status")
            ],
            jsScripts=[
                "/static/js/tickup.js",
                "/static/js/timeup.js",
                "/static/js/dataItemUpdater.js"
            ]
        )
