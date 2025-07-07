import datetime
from config.SettingsEnums import PressureType
from .AdminHtmlBuilder import AdminHtmlBuilder
from web.templates.components.WindBuilder import WindBuilder

from core.WeatherDisplay import WeatherDisplay
from config.WeatherConfig import WeatherConfig

def CurrentConditionsCard(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
    current = weatherDisplay.CurrentData
    tempAddon = "°F" if weatherConfig.Weather.Temperature.name == "F" else "°C"
    rainAddon = '"' if weatherConfig.Weather.Precipitation.name == "IN" else "mm"
    pressureAddon = 'mb' if weatherConfig.Weather.Pressure == PressureType.MB else 'in/hg'
    emoji = weatherDisplay.GetWeatherEmoji(current.State, current.ObservedTimeLocal.replace(tzinfo=None))
    pressureDisplay = ''
    if (not current.Pressure is None and current.Pressure > 1):
        pressureDisplay = F'{current.Pressure:.1f}</span><span class="data-addon">{pressureAddon}'
    else:
        pressureDisplay = F'No Pressure Recorded'

    sunDisplay = 'Daylight'
    if (weatherDisplay.IsSunset(datetime.now())):
        sunDisplay = 'Sunset'
    elif (weatherDisplay.IsSunrise(datetime.now())):
        sunDisplay = 'Sunrise'
    elif (weatherDisplay.IsNight(datetime.now())):
        sunDisplay = 'Night'

    secondsAgo = int((datetime.now() - current.LastUpdate).total_seconds())


    return f'''
    <div class="card mb-4 shadow-sm">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Current Conditions</h5>
            <span class="text-bold">Last Updated:</span> <span class="data-item" data-item="current-lastupdated">{current.LastUpdate.strftime("%b %d, %Y %I:%M:%S %p")}</span> (<span class="data-item tickup" data-item="current-updatedago" data-seconds="{secondsAgo}">{secondsAgo}s</span> <span class="data-addon">ago</span>) // <span class="text-bold">Last Queried:</span> <span class="data-item" data-item="current-lastquery">{datetime.now().strftime("%b %d, %Y %I:%M:%S %p")}</span> (<span class="data-item tickup" data-item="current-queryago" data-seconds="0">0s</span> <span class="data-addon">ago</span>)
        </div>
        <div class="card-body d-flex flex-row">
            <div class="p-2 align-items-center shadow-sm rounded">
                <div class="weather-emoji fs-1 data-item" data-item="current-emoji">{emoji['Emoji']}</div>
                <div class="weather-state data-item" data-item="current-state">{current.State or 'Unknown'}</div>
                <div class="weather-cloudcover"><span class="data-item" data-item="current-cloudcover">{current.CloudCover}</span><span class="data-addon">% Cloud Cover</span></div>
                <div class="weather-sun data-item" data-item="current-sun">{sunDisplay}</div>
            </div>
            <div class="p-2 fs-1 weather-temp">
                <span class="data-item" data-item="current-temp">{current.CurrentTemp:.1f}</span><span class="data-addon">{tempAddon}</span>
            </div>
            <div class="p-5 d-flex flex-column">
                <div class="p-0">
                    <span class="weather-feelslike-key fw-bold data-key">Feels Like:</span> <span class="weather-feelslike data-item" data-item="current-feelslike">{current.FeelsLike:.1f}</span><span class="data-addon">{tempAddon}</span>
                </div>
                <div class="p-0">
                    <span class="weather-heatindex-key fw-bold data-key">Heat Index:</span> <span class="weather-heatindex data-item" data-item="current-heatindex">{current.HeatIndex:.1f}</span><span class="data-addon">{tempAddon}</span>
                </div>
                <div class="p-0">
                    <span class="weather-dewpoint-key fw-bold data-key">Dew Point:</span> <span class="weather-dewpoint data-item" data-item="current-dewpoint">{current.DewPoint:.1f}</span><span class="data-addon">{tempAddon}</span>
                </div>
                <div class="p-0">
                    <span class="weather-pressure-key fw-bold">Pressure:</span> <span class="weather-pressure data-item" data-item="current-pressure">{pressureDisplay}</span>
                </div>
                <div class="p-0">
                    <span class="weather-precipitation-key fw-bold">Precipitation:</span> <span class="weather-precipitation data-item" data-item="current-precipitation">{current.Rain:.2f}</span><span class="data-addon">{rainAddon}</span>
                </div>
                <div class="p-0">
                    <span class="weather-humidity-key fw-bold">Humidity:</span> <span class="weather-humidity data-item" data-item="current-humidity">{current.Humidity}</span><span class="data-addon">%</span>
                </div>
            </div>
            <div class="p-2 d-flex justify-content-center align-items-center">
                {WindBuilder.WindCircle(weatherDisplay, weatherConfig)}
            </div>
        </div>
    </div>
    '''

def FutureForecastGrid(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
    rainAmounts = []
    hours = []
    rainBars = []
    weatherEmojis = []
    cloudCoverPercentages = []
    rainAddon = '"' if weatherConfig.Weather.Precipitation.name == "IN" else "mm"


    for hour in weatherDisplay.ForecastData.Next24Hours:
        time = datetime.strptime(hour.Time, "%Y-%m-%d %H:%M")
        hourTime = time.hour
        if (hourTime > 12):
            hourTime -= 12
        if (hourTime == 0):
            hourTime = 12
        timeLabel = str(hourTime) + time.strftime("%p")[0].lower()
        rain = hour.PrecipitationRain
        rainChance = hour.RainChance
        cloud = hour.CloudCoverPercentage

        barHeight = int(min(100, rainChance))
        emoji = weatherDisplay.GetWeatherEmoji(hour.ConditionText, time)
        rainDisplay = F"{rain:.2f}{rainAddon}" if rain > 0 else ""

        rainAmounts.append(F'<td class="rain-amount">{rainDisplay}</td>')
        hours.append(F'<td class="rain-hour">{timeLabel}</td>')
        rainBars.append(F'<td class="rain-bar"><div class="rain-baramount" style="height: {barHeight}%"></div></td>')
        weatherEmojis.append(F'<td class="rain-emoji">{emoji["Emoji"]}</td>')
        cloudCoverPercentages.append(F'<td class="rain-cloud">{cloud}%</td>')


    return f'''
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Future Conditions</h5>
            </div>
            <div class="card-body p-2">
                <table class="table rain-table">
                    <tr class="rain-amounts">
                        {"".join(rainAmounts)}
                    </tr>
                    <tr class="rain-hours">
                        {"".join(hours)}
                    </tr>
                    <tr class="rain-bars">
                        {"".join(rainBars)}
                    </tr>
                    <tr class="rain-emojis">
                        {"".join(weatherEmojis)}
                    </tr>
                    <tr class="rain-clouds">
                        {"".join(cloudCoverPercentages)}
                    </tr>
                </table>
            </div>
        </div>
    '''

class AdminDashboardHtmlBuilder:
    def Page(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig):
        return AdminHtmlBuilder.Page("Dashboard",
                                     F"""
                                        <div class="row">
                                            <div class="col-12">
                                                {CurrentConditionsCard(weatherDisplay, weatherConfig)}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-12">
                                                {FutureForecastGrid(weatherDisplay, weatherConfig)}
                                            </div>
                                        </div>
                                      """,
                                     weatherDisplay=weatherDisplay,
                                     weatherConfig=weatherConfig)
