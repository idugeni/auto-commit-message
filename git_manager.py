# git_manager.py
import subprocess
import logging
from typing import Optional, Dict, Any
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
            raise GitError("Current directory is not a Git repository")
        except FileNotFoundError:
            raise GitError("Git is not installed on the system")

    def get_diff(self) -> str:
        """Get staged changes from Git with enhanced error handling"""
        try:
            result = self._run_git_command(["diff", "--cached", "--no-color"], capture_output=True)
            diff_output = result.stdout.decode('utf-8').strip() if result.stdout else ""
            
            if diff_output:
                self.logger.debug(f"Successfully retrieved git diff ({len(diff_output)} bytes)")
                if len(diff_output) > 1024 * 1024:  # 1MB
                    self.logger.warning("Large diff detected (>1MB). This may impact performance.")
            else:
                self.logger.warning("No staged changes found. Please stage your changes using 'git add'")
                
            return diff_output
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
            raise GitError(f"Failed to get git diff: {error_msg}")
        except UnicodeDecodeError as e:
            raise GitError(f"Failed to decode git diff output: {str(e)}. Please check for binary files.")

    def get_stats(self) -> Dict[str, int]:
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
            # Return default values instead of None for consistency
            return {'files_changed': 0, 'insertions': 0, 'deletions': 0}

    def commit(self, message: str) -> bool:
        """Commit changes with the given message"""
        try:
            self._run_git_command(["commit", "-m", str(message)])
            self.logger.info("Changes committed successfully")
            return True
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to commit changes: {str(e)}")

    @staticmethod
    def _run_git_command(args: list, **kwargs) -> subprocess.CompletedProcess:
        """Run a Git command with given arguments"""
        try:
            return subprocess.run(["git"] + args, **kwargs, check=True)
        except subprocess.CalledProcessError as e:
            # Re-raise with more context
            error_msg = e.stderr.decode('utf-8').strip() if hasattr(e, 'stderr') and e.stderr else str(e)
            raise subprocess.CalledProcessError(
                e.returncode, 
                e.cmd, 
                output=e.output if hasattr(e, 'output') else None,
                stderr=f"Git command failed: {error_msg}"
            )