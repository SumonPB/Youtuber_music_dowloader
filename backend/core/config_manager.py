# config_manager.py
import os
import sys
import configparser
from pathlib import Path

def resource_path(relative_path):
    """Obtiene rutas correctas tanto en modo normal como empaquetado."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ConfigManager:
    def __init__(self):

        # Ruta correcta al archivo config.ini (soporta PyInstaller)
        self.config_path = Path(resource_path("backend/core/config.ini"))

        self.config = configparser.ConfigParser()

        self.default_config = {
            'settings': {
                # General
                'default_folder': str(Path.home() / 'Music'),
                'default_quality': '320',
                'theme': 'dark',

                # FFmpeg
                'ffmpeg_path': resource_path("backend/core/ffmpeg/bin/ffmpeg.exe"),

                # Monitor
                'monitor_browser': 'brave',
                'browser_path': 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
                'chromedriver_path': resource_path("backend/core/chromedriver.exe"),
                'user_profile': 'Default',
                'monitor_delay': '5',
                'debug_port': '9222'
            }
        }

        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            # Crea el archivo dentro del exe o carpeta temporal
            self.save_config(self.default_config)
        else:
            self.config.read(self.config_path)

            # Asegurar claves
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

        # Crear la carpeta si no existe (PyInstaller crea carpetas vacías)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            self.config.write(f)


# Singleton
config = ConfigManager()
