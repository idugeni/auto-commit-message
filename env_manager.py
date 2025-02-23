# env_manager.py
import os
from typing import Tuple, Optional
from dotenv import load_dotenv
from config import Config
from exceptions import EnvError

class EnvironmentManager:
    """Manage environment configuration"""
    @staticmethod
    def setup() -> Tuple[bool, Optional[str]]:
        """Set up environment and return API key"""
        if not Config.GLOBAL_ENV_PATH.exists():
            raise EnvError(f"Environment file not found at {Config.GLOBAL_ENV_PATH}")

        load_dotenv(Config.GLOBAL_ENV_PATH)
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise EnvError("GEMINI_API_KEY not found in environment file")

        return True, api_key