from dataclasses import dataclass


@dataclass
class ElementSettings:
    Enabled: bool = True
    X: int = 0
    Y: int = 0