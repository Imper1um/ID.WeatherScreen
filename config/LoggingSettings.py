from dataclasses import dataclass

@dataclass
class LoggingSettings:
    EnableTrace: bool = False
    EnableDebug: bool = False
    LoggingLevel: str = "INFO"