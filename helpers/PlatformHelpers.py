import logging
import platform


class PlatformHelpers:
    @staticmethod
    def IsRaspberryPi():
        uname = platform.uname()
        logging.debug(F"IsRaspberryPi: {platform.system()} == 'Linux' and '{uname.machine}'.startswith('aarch') == {uname.machine.startswith('aarch')}")
        return platform.system() == "Linux" and uname.machine.startswith("aarch")