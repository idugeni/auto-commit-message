import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

# Suppress gRPC and Abseil warnings (set once at the beginning)
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["GRPC_TRACE"] = ""

# Global path for .env.local
GLOBAL_ENV_PATH = r"C:\Tools\auto-commit-message\.env.local"

# Check if .env.local exists
if not os.path.exists(GLOBAL_ENV_PATH):
    print(f"❌ Error: .env.local file not found at {GLOBAL_ENV_PATH}")
    print("⚠️ Make sure you have saved your API key in the correct location.")
    exit(1)

# Load environment variables
load_dotenv(GLOBAL_ENV_PATH)

# Retrieve API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env.local")
    exit(1)

# Check if Git is installed
try:
    subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except FileNotFoundError:
    print("❌ Error: Git is not installed! Please install Git before running this script.")
    exit(1)

# Check if current directory is a Git repository
try:
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except subprocess.CalledProcessError:
    print("❌ Error: This directory is not a Git repository!")
    exit(1)

# Configure Gemini AI
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

def get_git_diff():
    """Retrieve staged changes in the Git repository."""
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout.strip() if result.stdout else None

def generate_commit_message(diff):
    """Generate a commit message based on the Git diff."""
    prompt = f"""Generate a Git commit message for the following changes:
    
    {diff}

    The commit message should follow this format:
    - The title must be at most 50 characters.
    - The description must be wrapped at 72 characters.
    - The title must start with one of the following types:
      - build, ci, chore, docs, feat, fix, perf, refactor, revert, style, test, security.
    - The title must be concise but descriptive.
    - The description should provide meaningful context.
    - Do not include any extra text, just return the formatted commit message without enclosing it in triple backticks."""
    
    try:
        response = chat_session.send_message(prompt)
        return response.text.strip().strip('`') if response else "Error generating commit message."
    except Exception as e:
        print(f"❌ Error while generating commit message: {e}")
        return "Error generating commit message."

def commit_changes(commit_message):
    """Commit changes with the generated message."""
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("✅ Changes committed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while committing changes: {e}")

def main():
    print(f"📂 Working directory: {os.getcwd()}")

    diff = get_git_diff()
    if not diff:
        print("⚠️ No staged changes found. Please use 'git add .' first.")
        return  # Exit without committing

    commit_message = generate_commit_message(diff)
    
    print(f"\nGenerated Commit Message:\n{commit_message}\n")
    
    commit_changes(commit_message)

if __name__ == "__main__":
    main()
