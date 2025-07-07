import threading, logging, secrets, os

from flask import Flask, request, redirect, url_for, session, render_template_string

from config.WeatherConfig import WeatherConfig
from core.WeatherDisplay import WeatherDisplay
from core.WeatherEncoder import WeatherEncoder
from services.WeatherService import WeatherService
from web.routes.AdminRoutes import AdminRoutes
from web.templates.admin import *

from .templates.BaseHtmlBuilder import BaseHtmlBuilder
from .templates.LoginHtmlBuilder import LoginHtmlBuilder

class WeatherWeb:
    def __init__(self, config: WeatherConfig, display: WeatherDisplay, encoder: WeatherEncoder, service: WeatherService):
        self.Config = config
        self.Log = logging.getLogger("WeatherWeb")

        staticFolder = os.path.join(os.path.dirname(__file__), "static")

        self.PublicApp = Flask("WeatherWebPublic")
        self.AdminApp = Flask("WeatherWebAdmin")
        self.AdminApp.secret_key = secrets.token_hex(16)
        self.AdminApp.static_folder = staticFolder
        self.AdminApp.static_url_path = "/static"
        self.Display = display
        self.Encoder = encoder
        self.Service = service
        self._setupRoutes()

    def _setupRoutes(self):
        self._setupPublicRoutes()
        self._setupAdminRoutes()

    def _setupPublicRoutes(self):
        @self.PublicApp.route("/")
        def public_root():
            return "Welcome to WeatherScreen Public Interface!"

    def _setupAdminRoutes(self):
        AdminRoutes.SetupAdminRoutes(self.AdminApp, self.Config, self.Display, self.Encoder, self.Service)

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

        self.Log.info(F"Starting Admin Web on port {self.Config.Web.AdminListenPort}")
        self.AdminThread = threading.Thread(
            target=self.AdminApp.run,
            kwargs={
                "host": "0.0.0.0",
                "port": self.Config.Web.AdminListenPort,
                "threaded": True,
                "use_reloader": False
                },
            daemon=True)
        self.AdminThread.start()