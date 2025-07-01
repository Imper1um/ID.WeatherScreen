import threading, logging

from flask import Flask

from config.WeatherConfig import WeatherConfig

class WeatherWeb:
    def __init__(self, config: WeatherConfig):
        self.Config = config
        self.Log = logging.getLogger("WeatherWeb")

        self.PublicApp = Flask("WeatherWebPublic")
        self.AdminApp = Flask("WeatherWebAdmin")

    def _setupRoutes(self):
        @self.PublicApp.route("/")
        def public_root():
            return "Welcome to WeatherScreen Public Interface!"

        @self.AdminApp.route("/")
        def admin_root():
            return "Welcome to WeatherScreen Admin Interface!"

    def start(self):
        if not self.Config.Web.Enabled:
            return

        self.Log.info(F"Starting Public Web on port {self.Config.Web.PublicListenPort}")
        self.PublicThread = threading.Thread(
            target=self.PublicApp.run,
            kwargs={
                "host": "0.0.0.0",
                "port": self.Config.Web.PublicListenPort,
                "threaded": True,
                "use_reloader": False
                },
            daemon=True)
        self.PublicThread.start()