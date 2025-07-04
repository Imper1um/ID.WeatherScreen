import logging
import platform

class Platform:
    Log = logging.getLogger("Platform")

    def IsRaspberryPi():
        uname = platform.uname()
        Platform.Log.debug(F"IsRaspberryPi: {platform.system()} == 'Linux' and '{uname.machine}'.startswith('aarch') == {uname.machine.startswith('aarch')}")
        return platform.system() == "Linux" and uname.machine.startswith("aarch")
