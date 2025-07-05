from .BaseHtmlBuilder import BaseHtmlBuilder
from .FormHtmlBuilder import FormHtmlBuilder

def Header():
    return F"""
        <h2 class="top-header">Weather Screen Admin Login</h2>
        """

class LoginHtmlBuilder:
    def Page():
        form = F"""
            <div class="row">
                <div class="col">
                    {FormHtmlBuilder.Password("Password", "password", "password")}
                </div>
            </div>
            <div class="row">
                <div class="col d-grid gap-2">
                    {FormHtmlBuilder.Submit("Login", "login", "btn-primary btn-login")}
                </div>
            </div>
        """
        return BaseHtmlBuilder.Page("Admin Login", F"""
                <div class="row">
                    <div class="col">
                        {Header()}
                    </div>
                </div>
                {BaseHtmlBuilder.ErrorSection()}
                <div class="row">
                    <div class="col">
                        {FormHtmlBuilder.Form(form, classes="form-login")}
                    </div>
                </div>
            """, bodyClasses="page-login", nav_title = "WeatherScreen Admin"
        )