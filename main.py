import os

# Set logging environment variables early
os.environ.update({
    "GRPC_VERBOSITY": "ERROR",
    "GLOG_minloglevel": "2",
    "GRPC_TRACE": ""
})

# Initialize absl logging
from absl import logging as absl_logging
absl_logging.set_verbosity(absl_logging.ERROR)

import sys
import logging_setup
import env_manager
import git_manager
import ai_manager
from exceptions import GitError, EnvError

def main():
    """Main function orchestrating the commit message generation process"""
    logger = logging_setup.LoggerSetup.setup()
    logger.debug(f"Working directory: {os.getcwd()}")

    try:
        logger.debug("Setting up environment")
        _, api_key = env_manager.EnvironmentManager.setup()

        git_manager_instance = git_manager.GitCommitManager(logger)
        ai_manager_instance = ai_manager.AIModelManager(api_key)

        if not git_manager_instance.check_prerequisites():
            sys.exit(1)

        diff = git_manager_instance.get_diff()
        if not diff:
            logger.warning("No staged changes found. Use 'git add <files>' first")
            sys.exit(0)

        logger.info("Generating commit message...")
        commit_message = ai_manager_instance.generate_commit_message(diff)
        
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

    except (GitError, EnvError) as e:
        logger.critical(str(e))
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()