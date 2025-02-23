# config.py
from pathlib import Path
from typing import Dict, List

class Config:
    """Configuration settings for the application"""
    GLOBAL_ENV_PATH = Path(r"C:\Tools\auto-commit-message\.env.local")
    MODEL_NAME = "gemini-2.0-flash-exp"
    GENERATION_CONFIG = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    COMMIT_TYPES = [
        "build", "ci", "chore", "docs", "feat", "fix",
        "perf", "refactor", "revert", "style", "test", "security"
    ]
    BREAKING_CHANGE_MARKER = "!"
    MAX_COMMIT_BODY_LENGTH = 72
    
    LOG_FORMAT = "[%(asctime)s] - [%(log_color)s%(levelname)s%(reset)s] : %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }