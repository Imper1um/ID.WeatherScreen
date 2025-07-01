from watchdog.events import FileSystemEventHandler
from WeatherConfig import WeatherConfig
import logging
import time

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, config: WeatherConfig, debounce_seconds: float = 1.0):
        self.Config = config
        self.Log = logging.getLogger("ConfigChangeHandler")
        self.LastModified = 0
        self.MinimumSeconds = debounce_seconds

    def on_modified(self, event):
        if event.src_path.endswith(self.Config._configFileName):
            now = time.time()
            if now - self.LastModified < self.MinimumSeconds:
                return
            self.LastModified = now

            self.Log.info("Config file modified. Attempting in-place reload.")
            try:
                self.Config.reload()
            except Exception as ex:
                self.log.warning(f"Config reload failed: {ex}")
