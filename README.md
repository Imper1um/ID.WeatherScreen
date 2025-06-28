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

### 3. Set Up Environment Variables

The application relies on several environment variables to function properly:

```bash
WEATHERAPI_KEY        # Your API key for WeatherAPI
WUNDERGROUND_KEY      # Your API key for Weather Underground
CHATGPT_KEY           # Your OpenAI API key – used for automated classification of weather background images
LOCATION              # Location string (e.g., "Orlando, FL")
WEATHER_STATION       # Specific station ID (e.g., "KFLORLAN65")
ENABLE_TRACE          # Set to "Yes" to enable trace-level logging
ENABLE_IMAGETAGS      # Set to "Yes" to display image tags on the screen. This is so you can figure out if you're missing an image type.
LOGGING_LEVEL=INFO    # Logging level: DEBUG, INFO, WARNING, etc.
```

> ⚠ If you're running the app interactively, you can `export` these variables or add them to your `~/.bashrc`.

> ⚠ **Important for Services:** Do **not** rely on `export` or `~/.bashrc` when running as a systemd service. These values must be explicitly included in the `.service` file (see below).

---

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
Environment="WEATHERAPI_KEY=your_weatherapi_key"
Environment="WUNDERGROUND_KEY=your_wunderground_key"
Environment="CHATGPT_KEY=your_chatgpt_api_key"
Environment="LOCATION=Your City, ST"
Environment="WEATHER_STATION=YourStationID"
Environment="ENABLE_TRACE=No"
Environment="LOGGING_LEVEL=INFO"
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