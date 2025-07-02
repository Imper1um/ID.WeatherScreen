from datetime import datetime


def TopHeader() -> str:
    return '''
        <!DOCTYPE html>
        <html>
        '''

def Header(title: str) -> str:
    return F'''
        <head>
            <title>{title}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js" integrity="sha384-ndDqU0Gzau9qJ1lfW4pNLlhNTkCfHzAVBReH9diLvGRem5+R9g2FzA8ZGN954O5Q" crossorigin="anonymous"></script>
            <link rel="stylesheet" type="text/css" href="/static/css/site.css">
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
        nav_items: list[tuple[str, str]] = []
    ):
        return F"""
            {TopHeader()}
            {Header(title)}
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

    def MiddleItem(type: str, title: str, content: str, dataContent: str = "", addon: str = "", classes: str = ""):
        addonDisplay = ""
        if (addon):
            addonDisplay = F'''
            <span class="middle-item-addon">{addon}</span>
            '''

        dataDisplay = ""
        if (dataContent):
            dataDisplay = F'''
                data-{type}="{dataContent}"
                '''
                
        return F'''
        <div class="{type} middle-item {classes}"><span class="middle-item-title">{title}:</span><span id="{type}" class="middle-item-data" {dataDisplay}>{content}</span>{addonDisplay}</div>
        '''