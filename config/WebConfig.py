import secrets, string

from dataclasses import dataclass, field

def generatePassword(length=8):
    charset = string.ascii_letters + string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))

@dataclass
class WebConfig:
    Enabled: bool = False
    PublicListenPort: int = 85
    PublicPassword: str = None
    AdminListenPort: int = 8585
    AdminPassword: str = field(default_factory=generatePassword)