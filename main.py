# Initialize absl logging first
from absl import logging as absl_logging
absl_logging.set_verbosity(absl_logging.ERROR)

import os

# Set logging environment variables early
os.environ.update({
    "GRPC_VERBOSITY": "ERROR",
    "GLOG_minloglevel": "2",
    "GRPC_TRACE": "",
    "GRPC_ENABLE_FORK_SUPPORT": "0",
    "GRPC_POLL_STRATEGY": "epoll1",
    "GRPC_DNS_RESOLVER": "native"
})

import sys
import logging_setup
import env_manager
import git_manager
import ai_manager
from exceptions import GitError, EnvError, APIError

def main():
    """Main function orchestrating the commit message generation process"""
    logger = logging_setup.LoggerSetup.setup()
    logger.debug(f"Working directory: {os.getcwd()}")

    try:
        logger.debug("Setting up environment")
        _, api_key = env_manager.EnvironmentManager.setup()

        try:
            git_manager_instance = git_manager.GitCommitManager(logger)
            git_manager_instance.check_prerequisites()
        except GitError as e:
            logger.critical(str(e))
            sys.exit(1)
            
        try:
            ai_manager_instance = ai_manager.AIModelManager(api_key)
        except APIError as e:
            logger.critical(f"API Error: {str(e)}")
            sys.exit(1)

        try:
            diff = git_manager_instance.get_diff()
            if not diff:
                logger.warning("No staged changes found. Use 'git add <files>' first")
                sys.exit(0)
        except GitError as e:
            logger.critical(str(e))
            sys.exit(1)

        logger.info("Generating commit message...")
        try:
            commit_message = ai_manager_instance.generate_commit_message(diff)
        except APIError as e:
            logger.critical(f"Failed to generate commit message: {str(e)}")
            sys.exit(1)
        
        from rich.prompt import Confirm
        from rich.console import Console
        from rich.panel import Panel
        from rich.style import Style
        
        console = Console()
        
        # Tampilkan statistik perubahan
        stats = git_manager_instance.get_stats()
        console.print(Panel(
            f"[bold blue]Files Changed:[/bold blue] {stats['files_changed']}\n" +
            f"[bold green]Insertions:[/bold green] +{stats['insertions']}\n" +
            f"[bold red]Deletions:[/bold red] -{stats['deletions']}",
            title="[bold]Commit Statistics[/bold]",
            border_style="blue"
        ))
        
        # Tampilkan dialog konfirmasi yang lebih menarik
        if not Confirm.ask(
            "[bold yellow]Proceed with this commit?[/bold yellow]",
            default=True,
            show_default=True
        ):
            console.print("[yellow]Commit canceled by user[/yellow]")
            sys.exit(0)
        
        if not git_manager_instance.commit(commit_message):
            sys.exit(1)

    except (GitError, EnvError, APIError) as e:
        logger.critical(str(e))
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()