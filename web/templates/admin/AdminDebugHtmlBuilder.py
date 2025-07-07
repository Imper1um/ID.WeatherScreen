from config.WeatherConfig import WeatherConfig
from core.WeatherDisplay import WeatherDisplay
from web.templates.admin.AdminHtmlBuilder import AdminHtmlBuilder

def NavTabs():
    return F'''
    <ul class="nav nav-tabs" id="adminDebugTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="tab-current-tab" data-bs-toggle="tab" data-bs-target="#tab-current" type="button" role="tab">Current Data</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-forecast-tab" data-bs-toggle="tab" data-bs-target="#tab-forecast" type="button" role="tab">Forecast Data</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-history-tab" data-bs-toggle="tab" data-bs-target="#tab-history" type="button" role="tab">History Data</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-sun-tab" data-bs-toggle="tab" data-bs-target="#tab-sun" type="button" role="tab">Sun Data</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-config-tab" data-bs-toggle="tab" data-bs-target="#tab-config" type="button" role="tab">Config</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="tab-logs-tab" data-bs-toggle="tab" data-bs-target="#tab-logs" type="button" role="tab">Logs</button>
      </li>
    </ul>
        '''

def DebugTab(section:str, isActive: bool = False):
    activeDisplay = "show active" if isActive else ""
    return F'''
    <div class="tab-pane fade {activeDisplay}" id="tab-{section}" role="tabpanel" aria-labelledby="tab-{section}-tab">
      <textarea id="textarea-{section}" class="form-control code-view" readonly></textarea>
      <div class="d-flex justify-content-end gap-2 mt-2">
        <button class="btn btn-primary" id="btnRetrieve-{section}">Retrieve</button>
        <button class="btn btn-success" id="btnPost-{section}" disabled>Post</button>
      </div>
    </div>
        '''

def LogsTab():
    return '''
        <div class="tab-pane fade" id="tab-logs" role="tabpanel" aria-labelledby="tab-logs-tab">
        <div class="mb-3 d-flex align-items-center gap-2">
          <select id="logDropdown" class="form-select w-auto">
            <option selected>--SELECT--</option>
          </select>
          <button class="btn btn-secondary" id="btnGetLogs">Get Logs</button>
        </div>
        <textarea id="logContent" class="form-control code-view" readonly></textarea>
      </div>
      '''


class AdminDebugHtmlBuilder:
    def Page(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig):
        return AdminHtmlBuilder.Page("Debug",
                                     F'''
                                        {NavTabs()}
                                        {DebugTab("current", True)}
                                        {DebugTab("forecast")}
                                        {DebugTab("history")}
                                        {DebugTab("sun")}
                                        {DebugTab("config")}
                                        {LogsTab()}
                                     ''',
                                     weatherDisplay=weatherDisplay,
                                     weatherConfig=weatherConfig)