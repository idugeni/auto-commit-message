# config.py
from pathlib import Path
import os
from typing import Dict, List

class Config:
    """Configuration settings for the application"""
    # Use platform-independent path for the environment file
    GLOBAL_ENV_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.local"))
    MODEL_NAME = "gemini-2.0-flash-thinking-exp-01-21"
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }
    COMMIT_TYPES = [
        "build", "ci", "chore", "docs", "feat", "fix",
        "perf", "refactor", "revert", "style", "test", "security"
    ]
    BREAKING_CHANGE_MARKER = "!"
    MAX_COMMIT_BODY_LENGTH = 72
    MAX_TITLE_LENGTH = 50
    COMMIT_SCOPE_PATTERN = r"^[a-z0-9-]+$"
    
    LOG_FORMAT = "%(log_color)s%(levelname)-8s%(reset)s │ %(asctime)s │ %(message)s"
    LOG_DATE_FORMAT = "%H:%M:%S"
    LOG_COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green,bold',
        'WARNING': 'yellow,bold',
        'ERROR': 'red,bold',
        'CRITICAL': 'red,bg_white,bold',
    }
    LOG_STYLES = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠',
        'ERROR': '✗',
        'CRITICAL': '☠'
    }