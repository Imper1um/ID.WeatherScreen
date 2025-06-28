from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from WeatherService import WeatherService
from WeatherDisplay import WeatherDisplay
from WeatherEncoder import WeatherEncoder
from datetime import datetime
import tkinter as tk
import logging
import os
import sys

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
WUNDERGROUND_KEY = os.getenv("WUNDERGROUND_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")
BASE_PATH = Path(__file__).resolve().parent

LOCATION = os.getenv("LOCATION")
WEATHER_STATION = os.getenv("WEATHER_STATION")
ENABLE_TRACE = os.getenv("ENABLE_TRACE", "No") == "Yes"
LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LEVEL, logging.INFO)

logDirectory = BASE_PATH / "logs"
logDirectory.mkdir(parents=True, exist_ok=True)

todayStr = datetime.now().strftime("%Y%m%d")
debugLogPath = logDirectory / f"WeatherDashboard_{todayStr}.Debug.log"
mainLogPath = logDirectory / f"WeatherDashboard_{todayStr}.log"

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

class DebugOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(LOG_LEVEL)
consoleHandler.setFormatter(formatter)

mainHandler = TimedRotatingFileHandler(
    mainLogPath, when="midnight", backupCount=30, encoding='utf-8')
mainHandler.setLevel(logging.INFO)
mainHandler.setFormatter(formatter)

debugHandler = TimedRotatingFileHandler(
    debugLogPath, when="midnight", backupCount=30, encoding='utf-8')
debugHandler.setLevel(logging.DEBUG)
debugHandler.setFormatter(formatter)
debugHandler.addFilter(DebugOnlyFilter())

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        consoleHandler,
        mainHandler,
        debugHandler
    ]
)

if (not ENABLE_TRACE):
    openai_lgoger = logging.getLogger("openai")
    openai_lgoger.setLevel(logging.WARNING)
    PILLogger = logging.getLogger("PIL.TiffImagePlugin")
    PILLogger.setLevel(logging.WARNING)
    urllibLogger = logging.getLogger("urllib3.connectionpool")
    urllibLogger.setLevel(logging.WARNING)

Log = logging.getLogger("ID.WeatherScreen")
Log.info("Started.")

if not WEATHERAPI_KEY:
    Log.fatal("Unable to start: There is no WEATHERAPI_KEY. This is needed to grab weather data.")
    sys.exit() 
if not LOCATION:
    Log.fatal("Unable to start: There is no LOCATION. This is needed to determine where the weather data is coming from.")
    sys.exit()

if WEATHER_STATION and not WUNDERGROUND_KEY:
    Log.warn("WEATHER_STATION is mentioned but there is no WUNDERGROUND_KEY. No weather updates can be made for this station. It doesn't prevent startup, but it will not show live data.")

weatherEncoder = None
if not CHATGPT_KEY:
    Log.info("No CHATGPT_KEY, so WeatherEncoder will not process unprocessed files!")
else:
    weatherEncoder = WeatherEncoder(CHATGPT_KEY)
    try:
        weatherEncoder.ProcessAllFiles()
        Log.info("WeatherEncoder is online.")
    except Exception as ex:
        Log.warn(F"WeatherEncoder failed, and so WeatherEncoder will not process unprocessed files! Check to make sure your CHATGPT_KEY has permission to execute queries, and that your CHATGPT_KEY has money in the account.")
        weatherEncoder = None

imageDirectory = os.path.join(BASE_PATH, "assets", "backgrounds")
if not os.path.exists(imageDirectory):
    Log.fatal("Unable to start: There is no assets/backgrounds folder. This needs to exist.")
    sys.exit()
if len(os.listdir(imageDirectory)) == 0:
    Log.fatal("Unable to start: There are no backgrounds in the assets/backgrounds folder. You need to have at least one background (preferably 1920x1080) to make this work.")
    sys.exit()

try:
    service = WeatherService(WEATHERAPI_KEY, LOCATION, WUNDERGROUND_KEY, WEATHER_STATION)
    root = tk.Tk()
    root.configure(bg="#00ff00")
    display = WeatherDisplay(root, service, weatherEncoder)
    display.StartDataRefresh()
    root.mainloop();
except:
    Log.exception(F"There was a serious error that crashed the WeatherScreen.")