import os
import subprocess
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('auto-commit-message')

# Suppress gRPC and Abseil warnings (set once at the beginning)
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["GRPC_TRACE"] = ""

# Configuration
GLOBAL_ENV_PATH = r"C:\Tools\auto-commit-message\.env.local"
MODEL_NAME = "gemini-2.0-flash"
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

def setup_environment() -> Tuple[bool, Optional[str]]:
    """
    Set up the environment by checking for necessary files and configurations.
    
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    # Check if .env.local exists
    if not os.path.exists(GLOBAL_ENV_PATH):
        return False, f"❌ Error: .env.local file not found at {GLOBAL_ENV_PATH}"

    # Load environment variables
    load_dotenv(GLOBAL_ENV_PATH)

    # Retrieve API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "❌ Error: GEMINI_API_KEY not found in .env.local"

    return True, api_key

def check_git_prerequisites() -> bool:
    """
    Check if Git is installed and the current directory is a Git repository.
    
    Returns:
        bool: True if prerequisites are met, False otherwise
    """
    # Check if Git is installed
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        logger.error("❌ Error: Git is not installed! Please install Git before running this script.")
        return False

    # Check if current directory is a Git repository
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("❌ Error: This directory is not a Git repository!")
        return False

    return True

def initialize_ai_model(api_key: str) -> genai.GenerativeModel:
    """
    Initialize and configure the Gemini AI model.
    
    Args:
        api_key (str): The API key for authentication
        
    Returns:
        genai.GenerativeModel: The initialized model instance
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=GENERATION_CONFIG,
    )

def get_git_diff() -> Optional[str]:
    """
    Retrieve staged changes in the Git repository.
    
    Returns:
        Optional[str]: The git diff output or None if no changes are staged
    """
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result.stdout.strip() if result.stdout else None

def generate_commit_message(model: genai.GenerativeModel, diff: str) -> str:
    """
    Generate a commit message based on the Git diff using the AI model.
    
    Args:
        model (genai.GenerativeModel): The AI model to use
        diff (str): Git diff content
        
    Returns:
        str: Generated commit message
    """
    if not diff:
        return "No changes to commit"
    
    chat_session = model.start_chat(history=[])
    
    prompt = f"""
    # Git Commit Message Generation Task

    ## Input: Git Diff
    ```diff
    {diff}
    ```

    ## Requirements
    Generate a professional Git commit message following these specific guidelines:

    1. Format:
       - Title: One line, max 50 characters
       - Blank line after title
       - Description: Multiple lines, each wrapped at 72 characters

    2. Title requirements:
       - Must start with one of these prefixes: {', '.join(COMMIT_TYPES)}
       - Must be concise but descriptive
       - Follow format: "<type>: <brief description>"

    3. Description requirements:
       - Provide meaningful context about what and why (not how)
       - Include relevant ticket/issue numbers if identifiable
       - Use imperative mood (e.g., "Add feature" not "Added feature")

    ## Output format
    <type>: <brief description>

    <detailed description>

    Note: Return ONLY the formatted commit message without any additional text, explanations, or code blocks.
    """
    
    try:
        response = chat_session.send_message(prompt)
        return response.text.strip().strip('`')
    except Exception as e:
        logger.error(f"❌ Error while generating commit message: {e}")
        return "Error generating commit message."

def commit_changes(commit_message: str) -> bool:
    """
    Commit changes with the generated message.
    
    Args:
        commit_message (str): The commit message to use
        
    Returns:
        bool: True if commit was successful, False otherwise
    """
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        logger.info("✅ Changes committed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error while committing changes: {e}")
        return False

def main():
    """Main function to orchestrate the commit message generation and git commit process."""
    logger.info(f"📂 Working directory: {os.getcwd()}")

    # Setup environment
    success, result = setup_environment()
    if not success:
        logger.error(result)
        sys.exit(1)
    api_key = result

    # Check Git prerequisites
    if not check_git_prerequisites():
        sys.exit(1)

    # Get git diff
    diff = get_git_diff()
    if not diff:
        logger.warning("⚠️ No staged changes found. Please use 'git add <files>' first.")
        sys.exit(0)

    # Initialize AI model
    model = initialize_ai_model(api_key)

    # Generate commit message
    commit_message = generate_commit_message(model, diff)
    
    # Display the generated message
    logger.info(f"\nGenerated Commit Message:\n{'-' * 50}\n{commit_message}\n{'-' * 50}\n")
    
    # Confirm with user
    user_response = input("Do you want to proceed with this commit message? (y/n): ").lower()
    if user_response not in ('y', 'yes'):
        logger.info("Commit canceled by user.")
        sys.exit(0)
    
    # Commit changes
    if not commit_changes(commit_message):
        sys.exit(1)

if __name__ == "__main__":
    main()