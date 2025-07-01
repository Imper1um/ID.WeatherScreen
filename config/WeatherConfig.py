import json
from dataclasses import dataclass, asdict, field
import dataclasses
from pathlib import Path
import logging
import collections.abc
from enum import Enum
from typing import List, Optional, get_origin, get_args, Union
from hashlib import md5

from config.LoggingSettings import LoggingSettings
from config.ServicesSettings import ServicesSettings
from config.ChatGPTSettings import ChatGPTSettings
from config.WeatherSettings import WeatherSettings

def from_dict(cls, data: dict):
    if not dataclasses.is_dataclass(cls):
        return data

    init_kwargs = {}

    for field in dataclasses.fields(cls):
        if not field.init:
            continue

        field_value = data.get(field.name, dataclasses.MISSING)
        if field_value is dataclasses.MISSING:
            continue

        field_type = field.type
        origin = get_origin(field_type)

        if origin is Union and type(None) in get_args(field_type):
            field_type = [t for t in get_args(field_type) if t != type(None)][0]

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            init_kwargs[field.name] = field_type(field_value)

        elif dataclasses.is_dataclass(field_type):
            init_kwargs[field.name] = from_dict(field_type, field_value)

        elif origin is list and get_args(field_type):
            item_type = get_args(field_type)[0]
            if dataclasses.is_dataclass(item_type):
                init_kwargs[field.name] = [from_dict(item_type, i) for i in field_value]
            elif isinstance(item_type, type) and issubclass(item_type, Enum):
                init_kwargs[field.name] = [item_type(i) for i in field_value]
            else:
                init_kwargs[field.name] = field_value

        else:
            init_kwargs[field.name] = field_value

    return cls(**init_kwargs)

def enum_safe_asdict(obj):
    if isinstance(obj, Enum):
        return obj.value
    elif dataclasses.is_dataclass(obj):
        result = {}
        for f in dataclasses.fields(obj):
            if f.metadata.get("serialize", True):
                value = getattr(obj, f.name)
                result[f.name] = enum_safe_asdict(value)
        return result
    elif isinstance(obj, dict):
        return {k: enum_safe_asdict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [enum_safe_asdict(v) for v in obj]
    else:
        return obj

def merge_missing_fields(default, user):
    if dataclasses.is_dataclass(default) and dataclasses.is_dataclass(user):
        for field in dataclasses.fields(default):
            if not field.init:
                continue
            default_value = getattr(default, field.name)
            user_value = getattr(user, field.name, None)
            if user_value is None:
                setattr(user, field.name, default_value)
            elif dataclasses.is_dataclass(default_value):
                merged = merge_missing_fields(default_value, user_value)
                setattr(user, field.name, merged)
            elif isinstance(default_value, list) and all(dataclasses.is_dataclass(i) for i in default_value):
                pass
        return user
    return user

def update_from_dict(self, new_data: dict):
    updated = from_dict(self.__class__, new_data)
    for field in dataclasses.fields(self):
        if field.init:
            setattr(self, field.name, getattr(updated, field.name))

@dataclass
class WeatherConfig:
    Logging: LoggingSettings = field(default_factory=LoggingSettings)
    Services: ServicesSettings = field(default_factory=ServicesSettings)
    ChatGPT: ChatGPTSettings = field(default_factory=ChatGPTSettings)
    Weather: WeatherSettings = field(default_factory=WeatherSettings)

    _configFileName: str = field(default="weatherscreen.config", init=False, repr=False, compare=False, metadata={"serialize":False})
    _basePath: Path = field(default=Path(__file__).resolve().parent, init=False, repr=False, compare=False, metadata={"serialize":False})
    _last_hash: Optional[str] = field(default=None, init=False, repr=False, compare=False, metadata={"serialize":False})

    @classmethod
    def load(cls) -> "WeatherConfig":
        config_path = cls._basePath / cls._configFileName
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    content = f.read()
                    data = json.loads(content)
                config = from_dict(cls, data)
                config._last_hash = md5(content).hexdigest()
                return config
            except Exception as e:
                logging.warning(f"Could not read config file: {e}")
                return cls()
        else:
            config = cls()
            config.save()
            return config


    def reload(self):
        config_path = self._basePath / self._configFileName
        if not config_path.exists():
            return

        try:
            with open(config_path, "rb") as f:
                content = f.read()
                current_hash = md5(content).hexdigest()

            if self._last_hash == current_hash:
                return

            data = json.loads(content)
            updated = from_dict(self.__class__, data)

            for field in dataclasses.fields(self):
                if field.init:
                    setattr(self, field.name, getattr(updated, field.name))

            self._last_hash = current_hash
            logging.getLogger("WeatherConfig").info("WeatherConfig reloaded (file changed).")

        except Exception as e:
            logging.getLogger("WeatherConfig").warning(f"Failed to reload WeatherConfig: {e}")

    def save(self):
        config_path = self._basePath / self._configFileName
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(enum_safe_asdict(self), f, indent=4)
        except Exception as e:
            logging.error(f"Could not save config file: {e}")

