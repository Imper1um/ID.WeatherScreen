from flask import Flask, request, redirect, url_for, session, render_template_string

from config import WeatherConfig
from core import WeatherDisplay, WeatherEncoder
from services.WeatherService import WeatherService
from web.templates import BaseHtmlBuilder, LoginHtmlBuilder
from web.templates.admin import *


class AdminRoutes:
    def SetupAdminRoutes(adminApp:Flask, config:WeatherConfig, display:WeatherDisplay, encoder:WeatherEncoder, service:WeatherService):
        @adminApp.before_request
        def CheckLogin():
            if request.endpoint == "login" or request.path.startswith("/static/"):
                return

            if not session.get("authenticated"):
                return redirect(url_for("login"))

        @adminApp.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                password = request.form.get("password")
                if (password == config.Web.AdminPassword):
                    session["authenticated"] = True
                    return redirect(url_for("admin_root"))
                else:
                    return render_template_string(LoginHtmlBuilder.Page(), error = "Incorrect password.")

            return render_template_string(LoginHtmlBuilder.Page())

        @adminApp.route("/debug")
        def debug():
            return render_template_string(AdminDebugHtmlBuilder.Page(display, config))

        @adminApp.route("/")
        def admin_root():
            return render_template_string(AdminDashboardHtmlBuilder.Page(display, config))