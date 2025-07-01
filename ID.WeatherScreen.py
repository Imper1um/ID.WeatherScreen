import tkinter as tk
import logging, os, sys, threading

from pathlib import Path
from watchdog.observers import Observer

from config.ConfigChangeHandler import ConfigChangeHandler
from logging.handlers import TimedRotatingFileHandler
from services.WeatherService import WeatherService
from core.WeatherDisplay import WeatherDisplay
from core.WeatherEncoder import WeatherEncoder
from config.WeatherConfig import WeatherConfig
from datetime import datetime

config = WeatherConfig.load()
config.save()

observer = Observer()
handler = ConfigChangeHandler(config)
observer.schedule(handler, path=str(config._basePath), recursive=False)

thread = threading.Thread(target=observer.start, daemon=True)
thread.start()

BASE_PATH = Path(__file__).resolve().parent

ENABLE_TRACE = config.Logging.EnableTrace
LEVEL = config.Logging.LoggingLevel.upper()
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
    pilPngLogger = logging.getLogger("PIL.PngImagePlugin")
    pilPngLogger.setLevel(logging.WARNING)

Log = logging.getLogger("ID.WeatherScreen")
Log.info("Started.")

if not config.Services.WeatherAPI.Key:
    Log.fatal("Unable to start: There is no Services.WeatherAPI.Key. This is needed to grab weather data.")
    sys.exit() 
if not config.Weather.Location:
    Log.fatal("Unable to start: There is no Weather.Location. This is needed to determine where the weather data is coming from.")
    sys.exit()

if config.Weather.StationCode and not config.Services.WeatherUnderground.Key:
    Log.warn("Weather.StationCode is mentioned but there is no Services.WeatherUnderground.Key. No weather updates can be made for this station. It doesn't prevent startup, but it will not show live data.")

weatherEncoder = None
if not config.ChatGPT.Key:
    Log.info("No ChatGPT.Key, so WeatherEncoder will not process unprocessed files!")
else:
    weatherEncoder = WeatherEncoder(config)
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

#try:
service = WeatherService(config)
root = tk.Tk()
root.configure(bg="#00ff00")
display = WeatherDisplay(root, service, weatherEncoder, config)
display.StartDataRefresh()
root.mainloop();
#except:
 #   Log.exception(F"There was a serious error that crashed the WeatherScreen.")