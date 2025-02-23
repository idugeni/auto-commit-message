"""
Auto Commit Message
----------------------------
A tool that uses AI to generate meaningful git commit messages based on staged changes.
"""

from config import Config
from exceptions import GitError, EnvError
from models import CommitType, CommitMessage
from logging_setup import LoggerSetup
from git_manager import GitCommitManager
from ai_manager import AIModelManager
from env_manager import EnvironmentManager

__version__ = "1.0.0-alpha"
__author__ = "Eliyanto Sarage"
__email__ = "officialelsa21@gmail.com"

# Define what should be available when using 'from package import *'
__all__ = [
    'Config',
    'GitError',
    'EnvError',
    'CommitType',
    'CommitMessage',
    'LoggerSetup',
    'GitCommitManager',
    'AIModelManager',
    'EnvironmentManager',
]

# Package metadata
PACKAGE_NAME = "auto-commit-message"
DESCRIPTION = "AI-powered Git commit message generator"