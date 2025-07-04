from datetime import datetime


def TopHeader() -> str:
    return '''
        <!DOCTYPE html>
        <html>
        '''

def Header(title: str, jsScripts: list[str] = None) -> str:
    scriptTags = ""
    if (jsScripts):
        scriptTags = "\n".join(
            F'<script src="{src}" defer></script>' for src in jsScripts)

    return F'''
        <head>
            <title>{title}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js" integrity="sha384-ndDqU0Gzau9qJ1lfW4pNLlhNTkCfHzAVBReH9diLvGRem5+R9g2FzA8ZGN954O5Q" crossorigin="anonymous"></script>
            <link rel="stylesheet" type="text/css" href="/static/css/site.css">
            {scriptTags}
        </head>
        '''

def NavBar(title: str, items: list[tuple[str, str]], middleContent: str = "", brandLink: str = "/") -> str:
    links = "\n".join(
        F'<li class="nav-item"><a class="nav-link" href="{url}">{text}</a></li>'
        for text, url in items
    )
    return F'''
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{brandLink}">{title}</a>
            {middleContent}
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {links}
                </ul>
            </div>
        </div>
    </nav>
    '''

def Body(content: str, middleContent: str = "", brandLink: str = "/", classes: str = "", style: str = "", nav_title: str = "", nav_items: list[tuple[str, str]] = []):
    return F'''
        <body class="page {classes}" style="{style}">
            {NavBar(nav_title, nav_items, middleContent=middleContent, brandLink=brandLink)}
            <div class="container">
                {content}
            </div>
        </body>
    '''

def Footer():
    return """
        </html>
        """

class BaseHtmlBuilder:
    def Page(
        title: str,
        content: str,
        brandLink: str = "/",
        middleContent: str = "",
        bodyClasses: str = "",
        bodyStyle: str = "",
        nav_title: str = "",
        nav_items: list[tuple[str, str]] = [],
        jsScripts: list[str] = None,
    ):
        return F"""
            {TopHeader()}
            {Header(title, jsScripts)}
            {Body(content, classes=bodyClasses, style=bodyStyle, nav_title=nav_title, nav_items=nav_items, brandLink=brandLink, middleContent=middleContent)}
            {Footer()}
        """

    def ErrorSection():
        return '''
            {% if error %}
            <div class="row">
                <div class="col alert alert-danger">
                    {{ error }}
                </div>
            </div>
            {% endif %}
        '''

    def MiddleContent(content: str, classes: str = "") -> str:
        return F'''
            <div class="d-none d-md-flex flex-grow-1 justify-content-center text-light gap-4 fs-6 middle-content {classes}" id="top-status-bar">
                {content}
            </div>
            '''

    def BuildLocalTime(time: datetime) -> str:
        hour = time.hour
        if (hour > 12):
            hour -= hour
        if (hour == 0):
            hour = 12
        ampm = time.strftime("%p").lower()
        timeDisplay = F"{hour}:{time.strftime("%M:%S")} {ampm}"
        return timeDisplay

    def BuildLocalDataTime(time: datetime) -> str:
        hour = time.hour
        minute = time.minute
        second = time.second
        ampm = "am" if hour < 12 else "pm"

        hour = hour % 12 or 12

        return f"{hour}:{minute:02}:{second:02}:{ampm}"

    def MiddleItem(type: str, title: str, content: str, dataContent: list[dict[str, str]] = None, addon: str = "", classes: str = "", dataClasses: str = ""):
        addonDisplay = ""
        if (addon):
            addonDisplay = F'''
            <span class="middle-item-addon">{addon}</span>
            '''

        dataAttributes = ""
        if (dataContent):
            for item in dataContent:
                key = item.get("key", "").strip()
                value = item.get("content", "")
                if key:
                    dataAttributes += f' data-{key}="{value}"'
                
        return F'''
        <div class="{type} middle-item {classes}"><span class="middle-item-title">{title}:</span><span id="{type}" class="middle-item-data {dataClasses}" {dataAttributes}>{content}</span>{addonDisplay}</div>
        '''