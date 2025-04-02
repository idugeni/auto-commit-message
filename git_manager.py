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
        """Get staged changes from Git with enhanced error handling"""
        try:
            result = self._run_git_command(["diff", "--cached", "--no-color"], capture_output=True)
            diff_output = result.stdout.decode('utf-8').strip() if result.stdout else None
            
            if diff_output:
                self.logger.debug(f"Successfully retrieved git diff ({len(diff_output)} bytes)")
                if len(diff_output) > 1024 * 1024:  # 1MB
                    self.logger.warning("Large diff detected (>1MB). This may impact performance.")
            else:
                self.logger.warning("No staged changes found. Please stage your changes using 'git add'")
                
            return diff_output
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
            self.logger.error(f"Failed to get git diff: {error_msg}")
            return None
        except UnicodeDecodeError as e:
            self.logger.error(f"Failed to decode git diff output: {str(e)}. Please check for binary files.")
            return None

    def get_stats(self) -> dict:
        """Get statistics of staged changes"""
        try:
            result = self._run_git_command(["diff", "--cached", "--numstat"], capture_output=True)
            stats_output = result.stdout.decode('utf-8').strip().split('\n')
            
            total_files = len([line for line in stats_output if line.strip()])
            total_insertions = 0
            total_deletions = 0
            
            for line in stats_output:
                if not line.strip():
                    continue
                parts = line.split()
                if parts[0] == '-' or parts[1] == '-':  # Binary file
                    continue
                total_insertions += int(parts[0])
                total_deletions += int(parts[1])
            
            return {
                'files_changed': total_files,
                'insertions': total_insertions,
                'deletions': total_deletions
            }
        except (subprocess.CalledProcessError, ValueError, IndexError) as e:
            self.logger.error(f"Failed to get git stats: {str(e)}")
            return {'files_changed': 0, 'insertions': 0, 'deletions': 0}

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