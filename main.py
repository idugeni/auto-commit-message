import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

# Path global untuk .env.local
GLOBAL_ENV_PATH = r"C:\Tools\auto-commit-message\.env.local"

# Periksa apakah .env.local ada di folder global
if not os.path.exists(GLOBAL_ENV_PATH):
    print(f"❌ Error: File .env.local tidak ditemukan di {GLOBAL_ENV_PATH}")
    print("⚠️ Pastikan Anda telah menyimpan API key di lokasi yang benar.")
    exit(1)

# Load environment variables dari .env.local global
load_dotenv(GLOBAL_ENV_PATH)

# Ambil API key dari environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY tidak ditemukan di .env.local")
    exit(1)

# Periksa apakah Git tersedia
try:
    subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except FileNotFoundError:
    print("❌ Error: Git tidak ditemukan! Pastikan Git telah diinstal di sistem Anda.")
    exit(1)

# Periksa apakah folder saat ini adalah repo Git
try:
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except subprocess.CalledProcessError:
    print("❌ Error: Direktori ini bukan repository Git!")
    exit(1)

# Konfigurasi model AI
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
    """Mendapatkan perubahan dalam repositori Git yang telah di-stage."""
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout.strip() if result.stdout else None

def generate_commit_message(diff):
    """Menghasilkan pesan commit dengan format yang sesuai."""
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
    """Melakukan commit dengan pesan yang dihasilkan."""
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("✅ Changes committed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while committing changes: {e}")

def main():
    print(f"📂 Working directory: {os.getcwd()}")

    diff = get_git_diff()
    if not diff:
        print("⚠️ Tidak ada perubahan yang di-*stage*. Silakan gunakan 'git add .' terlebih dahulu.")
        return  # Langsung keluar tanpa melakukan commit

    commit_message = generate_commit_message(diff)
    
    print(f"\nGenerated Commit Message:\n{commit_message}\n")
    
    commit_changes(commit_message)

    # Shutdown gRPC properly to avoid warnings
    os.environ["GRPC_VERBOSITY"] = "NONE"
    os.environ["GRPC_TRACE"] = ""

if __name__ == "__main__":
    main()
