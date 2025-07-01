from dataclasses import dataclass

@dataclass
class WebConfig:
    Enabled: bool = False
    PublicListenPort: int = 85
    AdminListenPort: int = 8585