import google.generativeai as genai
from config import Config
from models import CommitMessage
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel

class AIModelManager:
    """Manage AI model operations with precision and care."""
    def __init__(self, api_key: str):
        self.model = self._initialize_model(api_key)
        self.console = Console()

    @staticmethod
    def _initialize_model(api_key: str) -> genai.GenerativeModel:
        """Initialize and configure the Gemini AI model."""
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            generation_config=Config.GENERATION_CONFIG,
        )

    def generate_commit_message(self, diff: str) -> CommitMessage:
        """Generate commit message using the AI model with enhanced error handling and performance."""
        if not diff:
            return CommitMessage("chore: no changes to commit", "")
        
        if len(diff) > 1024 * 1024:  # 1MB
            raise ValueError("Diff size exceeds 1MB limit. Please make smaller commits.")

        prompt = self._create_prompt(diff)
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Generating commit message..."),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("Generating", total=100)
                
                # Simulate progress while waiting for AI response
                progress.update(task, advance=30)
                chat_session = self.model.start_chat(history=[])
                progress.update(task, advance=30)
                
                try:
                    response = chat_session.send_message(prompt)
                    progress.update(task, advance=30)
                except Exception as e:
                    raise Exception(f"Failed to send message to AI model: {str(e)}")
                
                if not response or not response.text:
                    raise Exception("Empty response received from AI model")
                
                commit_message = CommitMessage.parse(response.text.strip().strip('`'))
                if not any(commit_message.title.startswith(t + ":") for t in Config.COMMIT_TYPES):
                    raise ValueError(f"Tipe commit tidak valid. Harus salah satu dari: {', '.join(Config.COMMIT_TYPES)}")
                
                if len(commit_message.title) > Config.MAX_TITLE_LENGTH:
                    raise ValueError(
                        f"Judul commit terlalu panjang. Maksimal {Config.MAX_TITLE_LENGTH} karakter, " 
                        f"saat ini {len(commit_message.title)} karakter. Mohon persingkat judul commit Anda."
                    )
                
                progress.update(task, advance=10)
                
                # Display the generated message in a nice panel
                self.console.print(Panel(
                    f"[bold green]Title:[/bold green] {commit_message.title}\n\n" +
                    f"[bold green]Description:[/bold green]\n{commit_message.description}",
                    title="Generated Commit Message",
                    border_style="green"
                ))
                
                return commit_message
        except TimeoutError:
            raise Exception("AI model response timed out. Please try again.")
        except Exception as e:
            raise Exception(f"Failed to generate commit message: {str(e)}")


    @staticmethod
    def _create_prompt(diff: str) -> str:
        """Create a detailed prompt for the AI model to generate a commit message."""
        commit_types_str = ', '.join(Config.COMMIT_TYPES)
        return f"""
# Git Commit Message Generation Task

## Input: Git Diff
```diff
{diff}
```

## Requirements
Generate a professional Git commit message following these specific guidelines:

1. **Title Format (Required):**
   - Must start with one of these types: {commit_types_str}
   - Follow format: "<type>: <brief description>"
   - STRICT Maximum 50 characters - be concise and direct
   - Focus on the core change, avoid unnecessary words
   - Use imperative mood (e.g., "add" not "added")
   - If breaking change, append "!" after type
   - Examples:
     * "feat: add JWT auth" (preferred)
     * "feat: add user authentication system" (too long)

2. **Description Format (Required if changes are significant):**
   - Leave one blank line after title
   - Wrap each line at 72 characters
   - Explain WHAT changed and WHY (not HOW)
   - Use bullet points for multiple changes
   - Include technical details when relevant
   - Example:
     "Implement JWT-based authentication to secure API endpoints.
     This change improves security by validating user sessions
     and preventing unauthorized access."

3. **Footer Format (Required for references):**
   - Leave one blank line before footer
   - Use these prefixes:
     * "Refs: #<issue-number>" for related issues
     * "Closes: #<issue-number>" for issues this commit resolves
     * "BREAKING CHANGE:" for breaking changes
   - One item per line
   - Example:
     "Refs: #123
     Closes: #456
     BREAKING CHANGE: API authentication required for all endpoints"

## Output Format
<type>: <brief description>

<detailed description>

<footer>

**Note:** Return ONLY the formatted commit message without any additional text or code blocks.
"""
