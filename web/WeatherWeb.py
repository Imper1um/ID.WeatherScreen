from io import BytesIO
import threading, logging, secrets, os

from datetime import datetime
import traceback
from PIL import Image, ImageDraw
from flask import Flask, request, redirect, send_file, url_for, session, render_template_string
from flask.json import jsonify

from config.WeatherConfig import WeatherConfig
from core.WeatherDisplay import WeatherDisplay
from core.WeatherEncoder import WeatherEncoder
from services.WeatherService import WeatherService
from web.templates import AdminDashboardHtmlBuilder, AdminHtmlBuilder

from .templates.BaseHtmlBuilder import BaseHtmlBuilder
from .templates.LoginHtmlBuilder import LoginHtmlBuilder
from .templates.AdminHtmlBuilder import AdminHtmlBuilder
from .templates.AdminDashboardHtmlBuilder import AdminDashboardHtmlBuilder

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

        self.LastRender = None

    def _setupRoutes(self):
        self._setupPublicRoutes()
        self._setupAdminRoutes()

    def _setupPublicRoutes(self):
        @self.PublicApp.route("/")
        def public_root():
            return "Welcome to WeatherScreen Public Interface!"

    def _setupAdminRoutes(self):
        @self.AdminApp.before_request
        def CheckLogin():
            if request.endpoint == "login" or request.path.startswith("/static/"):
                return

            if not session.get("authenticated"):
                return redirect(url_for("login"))

        @self.AdminApp.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                password = request.form.get("password")
                if (password == self.Config.Web.AdminPassword):
                    session["authenticated"] = True
                    return redirect(url_for("admin_root"))
                else:
                    return render_template_string(LoginHtmlBuilder.Page(), error = "Incorrect password.")

            return render_template_string(LoginHtmlBuilder.Page())

        @self.AdminApp.route("/")
        def admin_root():
            return render_template_string(AdminDashboardHtmlBuilder.Page(self.Display, self.Config))

        @self.AdminApp.route("/currentscreen.png")
        def currentScreenImage():
            if (self.LastRender):
                return self.LastRender
            try:
                width, height = 1920, 1080
                img = Image.new("RGB", (width, height), "#0F0")
                draw = ImageDraw.Draw(img)
                self.Display.Render(draw, drawType = "image")

                buf = BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)

                self.LastRender = send_file(buf, mimetype="image/png");
                return self.LastRender;
            except Exception as e:
                self.Log.warning(f"Error rendering current screen: {e}")
                self.Log.warning(traceback.format_exc())
                return ("Failed to render image", 500)

        @self.AdminApp.route("/api/current-data")
        def api_current_data():
            try:
                current = self.Service.GetCurrentData()
                emoji = self.Display.GetWeatherEmoji(current.State, current.ObservedTimeLocal)
                now = datetime.now()
                timeDisplay = BaseHtmlBuilder.BuildLocalTime(now)
                timeData = BaseHtmlBuilder.BuildLocalDataTime(now)
                uptime_seconds = self.Display.GetUptimeSeconds()
                uptime_string = self.Display.GetUptimeString()
                sunDisplay = 'Daylight'
                if (self.Display.IsSunset(datetime.now())):
                    sunDisplay = 'Sunset'
                elif (self.Display.IsSunrise(datetime.now())):
                    sunDisplay = 'Sunrise'
                elif (self.Display.IsNight(datetime.now())):
                    sunDisplay = 'Night'

                secondsAgo = int((datetime.now() - current.LastUpdate).total_seconds())
                pressure = "No Pressure Info"
                if (current.Pressure > 1):
                    pressure = F"{current.Pressure:.1f}"

                response = {
                    "current-emoji": { "content": emoji["Emoji"] },
                    "current-state": { "content": current.State },
                    "current-cloudcover": { "content": f"{current.CloudCover}" },
                    "current-temp": { "content": f"{current.CurrentTemp:.1f}" },
                    "current-feelslike": { "content": f"{current.FeelsLike:.1f}" },
                    "current-heatindex": { "content": f"{current.HeatIndex:.1f}" },
                    "current-dewpoint": { "content": f"{current.DewPoint:.1f}" },
                    "current-pressure": { "content": pressure },
                    "current-precipitation": { "content": f"{current.Rain:.2f}" },
                    "current-humidity": {"content": f"{current.Humidity}"},
                    "current-sun": { "content": sunDisplay },

                    "localtime": {
                        "content": timeDisplay,
                        "data": [{"key": "data-time", "content": timeData}]
                    },
                    "uptime": {
                        "content": uptime_string,
                        "data": [{"key": "data-seconds", "content": str(uptime_seconds)}]
                    },
                    "current-lastupdated": {"content":current.LastUpdate.strftime("%b %d, %Y %I:%M:%S %p")},
                    "current-lastquery": {"content":datetime.now().strftime("%b %d, %Y %I:%M:%S %p")},
                    "updatedago": {
                        "content": str(secondsAgo) + "s",
                        "data": [{"key": "data-seconds", "content": str(secondsAgo)}]
                     },
                    "queryago": {
                        "content": "0s",
                        "data": [{"key": "data-seconds", "content": "0"}]
                     }
                }

                return jsonify(response)

            except Exception as e:
                self.Log.warning(f"Failed to build current-data response: {e}")
                
                return jsonify({}), 500



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