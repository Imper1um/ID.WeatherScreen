from dataclasses import dataclass

@dataclass
class SkyGradientSettings:
    Enable: bool = True
    EnableCloud: bool = True
    CloudHeight: int = 8