# config_manager.py
import os
import configparser
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / 'config.ini'
        self.config = configparser.ConfigParser()

        # Ruta dinámica a FFmpeg dentro del proyecto
        ffmpeg_default_path = str(self.base_dir / "ffmpeg" / "bin" / "ffmpeg.exe")

        self.default_config = {
            'settings': {
                # General
                'default_folder': str(Path.home() / 'Music'),
                'default_quality': '320',
                'theme': 'dark',

                # FFmpeg
                'ffmpeg_path': ffmpeg_default_path,

                # Monitor
                'monitor_browser': 'brave',
                'browser_path': 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
                'chromedriver_path': str(self.base_dir / 'chromedriver.exe'),
                'user_profile': 'Default',
                'monitor_delay': '5',
                'debug_port': '9222'
            }
        }

        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            self.save_config(self.default_config)
        else:
            self.config.read(self.config_path)

            # Asegurar que existan todas las claves
            for section, options in self.default_config.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for key, value in options.items():
                    if not self.config.has_option(section, key):
                        self.config.set(section, key, value)

            self.save_config()

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save_config()

    def save_config(self, config_dict=None):
        if config_dict:
            self.config.read_dict(config_dict)
        with open(self.config_path, 'w') as f:
            self.config.write(f)

# Singleton
config = ConfigManager()
