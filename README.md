# ID.WeatherScreen
This is a Python-based weather screen. This screen is intended to run on a Raspberry Pi (tested on Pi 5, but could work on any machine).

![Screenshot](documentation/img/WeatherScreenApp.png)

This system uses multiple sources for data, and requires a bit of setup in order to get working, and is not intended to be used by people without knowledge about environment variables.

## 🌍 Environment Variables
To run this project correctly, you'll need to configure several environment variables. These control API access, location settings, logging levels, and optional debugging features.

### Required

| Variable           | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `WEATHERAPI_KEY`   | API key for accessing [WeatherAPI](https://www.weatherapi.com/). Used for retrieving general weather data. You will need to create an account (free). This project only accesses WeatherAPI once every 15 minutes, and 3 times upon startup, so the Free Tier should be fine. |
| `LOCATION`         | The name or code for the location (e.g., `Orlando, FL`) that you want to monitor or display weather data for. This can be a city name, a zip code, or coordinates. |

### Optional

| Variable           | Default | Description |
|--------------------|---------|-------------|
| `CHATGPT_KEY`      |         | OpenAI API key for automatically classifying images for use. |
| `ENABLE_TRACE`     | `No`    | If set to `Yes`, enables detailed trace logging for debugging purposes. |
| `LOGGING_LEVEL`    | `INFO`  | Adjusts the verbosity of logs. Accepted values include `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. |
| `WUNDERGROUND_KEY` |         | API key for accessing [Weather Underground](https://www.wunderground.com/weather/api). Provides data from personal weather stations. |
| `WEATHER_STATION`  |         | The station ID used to pull precise readings from a specific weather station (typically a WU station code like `KFLORLAN213`). |

NOTE: If you intend to use WUnderground, you will need to also mention a valid WEATHER_STATION code.


## Raspberry Pi 5 Setup Instructions

### 1. Install Required Python Packages

Ensure your Raspberry Pi is running Python 3 and has `pip` installed. Then install the project dependencies:

```bash
cd /path/to/ID.WeatherStation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This will create a virtual environment and install all required packages into it.

### 2. (Optional) Hide the Taskbar for a Clean Display

To enable autohide on the taskbar and create a more polished, kiosk-style appearance:

```bash
sudo apt install lxappearance
```

Then:

1. Open the terminal.
2. Run `lxappearance` or manually edit the file at `~/.config/lxpanel/LXDE-pi/panels/panel`.
3. Set `autohide=1` in the appropriate section.
4. Reboot to apply the changes.

### 3. (⚠ Deprecated) Set Up Environment Variables

> ⚠ Environment Variables are no longer supported as how the program is supplied data. See Settings below!

### 4. Install as a Systemd Service (Optional)

To launch the weather screen automatically at boot into a full-screen graphical session:

1. Create a systemd service file at `/etc/systemd/system/idweatherscreen.service`:

```ini
[Unit]
Description=Weather Dashboard Fullscreen
After=graphical-session.target
Wants=graphical-session.target

[Service]
ExecStart=/bin/bash -c 'sleep 10 && cd /path/to/source && source venv/bin/activate && export DISPLAY=:0 && python3 ID.WeatherScreen.py'
WorkingDirectory=/path/to/source
Environment="XDG_RUNTIME_DIR=/run/user/1000"
Restart=always
User=pi

[Install]
WantedBy=graphical.target
```

> ⚠ Replace `/path/to/source` with the full path to your cloned `ID.WeatherStation` directory.

2. Reload systemd and enable the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable idweatherscreen.service
sudo systemctl start idweatherscreen.service
```

## Background Images & EXIF Classification

The `ID.WeatherStation` dashboard dynamically selects a background image that matches the current weather and time of day. To function properly, the following must be observed:

### 1. Required Folder and Formats

You must place at least one image (`.jpg`, `.jpeg`, or `.png`) into the following directory:

```
/assets/backgrounds
```

Due to licensing restrictions, no default backgrounds are included in this repository. You are responsible for supplying your own images.

### 2. Image Tagging for Weather-Based Selection

To allow the system to intelligently choose an image based on weather conditions, each image must be tagged with appropriate EXIF metadata, depending on the file type:

- JPEG/JPG: Tags are stored in the `Keywords` field.
- PNG: Tags are stored in the `Tags` field.

Each image must include:

- Time Tag (choose one):
  - `Daylight`, `Night`, `Sunrise`, `Sunset`
- Weather Tag (choose one):
  - `Clear`, `PartlyCloudy`, `Overcast`, `Foggy`, `Lightning`, `LightRain`, `MediumRain`, `HeavyRain`, `Snow`

If images are not properly tagged, they will not be considered for weather/time selection.

You may use tools like ExifTool to manually apply these tags.

### 3. Automatic Tagging with ChatGPT (Optional)

If you set up `CHATGPT_KEY` with a valid OpenAI API key, the system will automatically tag new images:

- Place your untagged images in:
  ```
  /assets/unprocessed
  ```
- The application will analyze each image using GPT, determine the appropriate tags, encode the EXIF metadata, and move the processed image to:
  ```
  /assets/backgrounds
  ```

This automated classification process is optional but highly recommended for large image sets.

### 4. Fallback Behavior

If no images match the current weather and time requirements, the dashboard will:

- Randomly select any image from `/assets/backgrounds`, regardless of its tags.
- This is the only scenario where improperly tagged images may be used.

### 5. Recommended Image Size

Images should ideally match the resolution of your display (for example, 1920x1080 for 1080p screens), but non-matching resolutions are still supported.

# Settings and Configuration

> ⚠️ Environment Variables are no longer used for configuring this project. Configuration is now handled exclusively via a `.config` file.

## First Run

On the first run, the system will automatically generate a configuration file named:
```
weatherscreen.config
```

This file is saved in the same directory as the Python scripts. It contains all the necessary configuration for your weather display and must be edited to suit your needs. If the file does not exist, it will be created with default values.

## Configuration Sections

The configuration file is divided into several sections, each with a specific purpose:

### `Logging`

Controls the logging and debug output.

- `EnableTrace`: Enables more verbose internal tracing.
- `EnableDebug`: Enables detailed debug output.
- `LoggingLevel`: One of `"INFO"`, `"DEBUG"`, etc. Sets the minimum logging level.

### `Services`

Contains API keys and data provider selections.

#### `WeatherAPI` / `WeatherUnderground`

- `Key`: Your API key for each service.

#### `Selections`

Specifies which service is used for each data type.

- `History`: Provider for historical weather data. (Possible Values: WeatherUnderground)
- `Forecast`: Provider for forecast data. (Possible Values: WeatherAPI)
- `Sun`: Provider for sunrise/sunset calculations. (Possible Values: SunriseSunset)
- `Current`: A prioritized list of providers for current weather data (e.g. `["WeatherAPI", "WeatherUnderground"]`). The first provider will provide the base data, and then subsequent providers will overlay their data.

### `ChatGPT`

Specifies ChatGPT integration for image tagging.

- `Key`: Your OpenAI API key.
- `Model`: Model to use (e.g., `"gpt-4o"`).

### `Weather`

Main settings related to display and measurement preferences.

- `Location`: Location. This can be a Zip Code, a City, State, or a Latitude,Longitude value.
- `StationCode`: Station code (e.g., Weather Underground personal weather station ID).
- `Temperature`: `"F"` for Fahrenheit or `"C"` for Celsius.
- `Pressure`: `"MB"` for millibars or `"HG"` for inches of mercury.
- `Wind`: `"MPH"` or `"KPH"`.
- `Visibility`: `"Miles"` or `"Kilometers"`.
- `Precipitation`: `"MM"` for millimeters or `"IN"` for inches.

These fields control how the system interprets and formats raw weather data.

### `Weather` → Display Text Elements

These settings control the on-screen position and style of individual weather-related text elements. Each setting is an object with fields like:

- `X`, `Y`: Coordinates relative to the top-left of the screen (Tkinter coordinate system).
- `FillColor`: Hex or named color (e.g. `"#FFF"`, `"red"`).
- `FontFamily`: Optional font name.
- `FontWeight`: Can be `"normal"` or `"bold"`.
- `FontSize`: Size of the text in points.
- `Anchor`: Text anchor (`"center"`, `"e"`, `"ne"`, etc.).
- `Stroke`: If `True`, applies a 2px stroke outline around the text for better readability.
- `Enabled`: Whether the element is drawn on the canvas.

#### Common Elements

- `ImageTags`: Debug element that shows the actual weather tags used to pick a background image. For instance, if the system wanted `["Cloudy", "Daylight"]` but got `["Lightning", "Night"]`, those would show here.
- `Uptime`: Displays system uptime.
- `LastUpdated`: Shows the time of the most recent data update.
- `Observed`: Time of the observed weather report.
- `Source`: Which data source provided the weather data.
- `DayOfWeek`, `FullDate`, `Time`: Display current day/date/time with optional formatting.
- `Station`: Shows the station name or ID.
- `CurrentTempEmoji`: A weather-related emoji icon next to the temperature.
- `CurrentTemp`: Displays the current temperature.
- `FeelsLike`: Displays the "feels like" temperature.
- `TempHigh` / `TempLow`: Displays high and low forecasted temperatures.

Other Customizable elements will be added in the future.