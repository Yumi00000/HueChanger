import json
import logging
from pathlib import Path
from typing import List, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class Config:
    # Default to a common Linux font if Akrobat-Bold.otf is missing
    DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def __init__(self):
        self.zero_spec: int = 0
        self.max_spec: int = 360
        self.change_num: int = 50
        self.full_progress: int = 100
        self.font_path: str = "assets/Akrobat-Bold.otf"  # Relative path, adjustable
        self.check_add_text_box: bool = False
        self.bg_color: str = "white"
        self.high_text_color_check: bool = False
        self.high_text_color: str = "black"
        self.down_text_color: str = "#8B0000"
        self.slogans: List[Tuple[str, str]] = [
            ("NO ALCOHOL CHALLENGE", "ACCORDING TO THE AGE"),
            ("NO LATE EATING CHALLENGE", "ACCORDING TO THE AGE"),
            ("NO CHEAT CHALLENGE", "ACCORDING TO THE AGE"),
            ("NO SUGAR CHALLENGE", "ACCORDING TO THE AGE"),
            ("NO BAD FAT CHALLENGE", "ACCORDING TO THE AGE"),
        ]

    def validate(self) -> None:
        """Validate configuration values, with forgiving font validation."""
        if not (0 <= self.zero_spec <= 360):
            raise ConfigError("zero_spec must be between 0 and 360")
        if not (0 <= self.max_spec <= 360):
            raise ConfigError("max_spec must be between 0 and 360")
        if self.change_num <= 0:
            raise ConfigError("change_num must be positive")
        if not self.slogans:
            raise ConfigError("At least one slogan is required")

        # Check font path, fall back to default if invalid
        if not Path(self.font_path).is_file():
            logger.warning(f"Font file not found: {self.font_path}. Falling back to {self.DEFAULT_FONT_PATH}")
            if Path(self.DEFAULT_FONT_PATH).is_file():
                self.font_path = self.DEFAULT_FONT_PATH
            else:
                logger.warning(f"Default font {self.DEFAULT_FONT_PATH} not found. Text rendering may fail.")

    def to_dict(self) -> dict:
        """Convert config to dictionary for serialization."""
        return {
            "zero_spec": self.zero_spec,
            "max_spec": self.max_spec,
            "change_num": self.change_num,
            "full_progress": self.full_progress,
            "font_path": self.font_path,
            "check_add_text_box": self.check_add_text_box,
            "bg_color": self.bg_color,
            "high_text_color_check": self.high_text_color_check,
            "high_text_color": self.high_text_color,
            "down_text_color": self.down_text_color,
            "slogans": self.slogans,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config instance from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class ConfigFactory:
    DEFAULT_CONFIG_PATH = "config.json"

    @staticmethod
    def create_config(config_path: str = None) -> Config:
        """Create a Config instance, loading from file if available."""
        config = Config()
        config_path = config_path or ConfigFactory.DEFAULT_CONFIG_PATH

        if Path(config_path).is_file():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                config = Config.from_dict(data)
            except (json.JSONDecodeError, ConfigError) as e:
                raise ConfigError(f"Failed to load config from {config_path}: {str(e)}")

        try:
            config.validate()
        except ConfigError as e:
            raise ConfigError(f"Invalid configuration: {str(e)}")

        return config

    @staticmethod
    def save_config(config: Config, config_path: str = None) -> None:
        """Save configuration to a file."""
        config_path = config_path or ConfigFactory.DEFAULT_CONFIG_PATH
        try:
            with open(config_path, "w") as f:
                json.dump(config.to_dict(), f, indent=4)
        except IOError as e:
            raise ConfigError(f"Failed to save config to {config_path}: {str(e)}")