import os
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
        
        logger.info(f"\nGenerated Commit Message:\n{'-' * 50}\n{commit_message}\n{'-' * 50}")
        
        if input("Proceed with this commit message? (y/n): ").lower() not in ('y', 'yes'):
            logger.info("Commit canceled by user")
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