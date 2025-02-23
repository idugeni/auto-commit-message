# git_manager.py
import subprocess
import logging
from typing import Optional
from exceptions import GitError

class GitCommitManager:
    """Manage Git operations"""
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def check_prerequisites(self) -> bool:
        """Check Git installation and repository status"""
        try:
            self._run_git_command(["--version"])
            self._run_git_command(["rev-parse", "--is-inside-work-tree"])
            self.logger.debug("Git prerequisites check passed")
            return True
        except subprocess.CalledProcessError:
            self.logger.critical("Current directory is not a Git repository")
            return False
        except FileNotFoundError:
            self.logger.critical("Git is not installed on the system")
            return False

    def get_diff(self) -> Optional[str]:
        """Get staged changes from Git"""
        try:
            result = self._run_git_command(["diff", "--cached"], capture_output=True)
            diff_output = result.stdout.decode('utf-8').strip() if result.stdout else None
            
            if diff_output:
                self.logger.debug("Successfully retrieved git diff")
            else:
                self.logger.warning("No staged changes found")
                
            return diff_output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get git diff: {str(e)}")
            return None

    def commit(self, message: str) -> bool:
        """Commit changes with the given message"""
        try:
            self._run_git_command(["commit", "-m", str(message)])
            self.logger.info("Changes committed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit changes: {str(e)}")
            return False

    @staticmethod
    def _run_git_command(args: list, **kwargs) -> subprocess.CompletedProcess:
        """Run a Git command with given arguments"""
        return subprocess.run(["git"] + args, **kwargs, check=True)