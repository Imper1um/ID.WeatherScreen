from .AdminHtmlBuilder import AdminHtmlBuilder

from core.WeatherDisplay import WeatherDisplay
from config.WeatherConfig import WeatherConfig

class AdminDashboardHtmlBuilder:
    def Page(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig):
        return AdminHtmlBuilder.Page("Dashboard",
                                     "Dashboard content TBA",
                                     weatherDisplay=weatherDisplay,
                                     weatherConfig=weatherConfig)
