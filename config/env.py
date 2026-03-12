# config/env.py
# Разделение сред: local / production
import os

ENV = os.getenv("ZAVOT_ENV", "local")

CONFIG = {
    "local": {
        "DB_TYPE": "sqlite",
        "DB_PATH": os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'ZAVot.db'),
        "SECRET_KEY": "dev-secret-key",
        "DEBUG": True,
        "HOST": "127.0.0.1",
        "PORT": 5000,
        "YD_BASE_FOLDER": "disk:/ZAVot_data",
        "YD_TOKEN": os.getenv("YD_TOKEN", ""),
    },
    "production": {
        "DB_TYPE": "mysql",
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": int(os.getenv("DB_PORT", 3306)),
        "DB_NAME": os.getenv("DB_NAME", "zavot"),
        "DB_USER": os.getenv("DB_USER", "zavot"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "SECRET_KEY": os.getenv("SECRET_KEY", "change-me-in-production"),
        "DEBUG": False,
        "HOST": "0.0.0.0",
        "PORT": int(os.getenv("PORT", 8080)),
        "YD_BASE_FOLDER": "disk:/ZAVot_data",
        "YD_TOKEN": os.getenv("YD_TOKEN", ""),
    }
}

def get_config():
    return CONFIG.get(ENV, CONFIG["local"])