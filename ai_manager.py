import google.generativeai as genai
from config import Config
from models import CommitMessage
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from exceptions import APIError

class AIModelManager:
    """Manage AI model operations with precision and care."""
    def __init__(self, api_key: str):
        self.console = Console()
        self.model = self._initialize_model(api_key)

    @staticmethod
    def _initialize_model(api_key: str) -> genai.GenerativeModel:
        """Initialize and configure the Gemini AI model."""
        if not api_key or not isinstance(api_key, str) or len(api_key) < 10:
            raise APIError("Invalid API key format. Please check your API key.")
            
        try:
            genai.configure(api_key=api_key)
            # Validate API key with a simple operation
            genai.list_models()
            return genai.GenerativeModel(
                model_name=Config.MODEL_NAME,
                generation_config=Config.GENERATION_CONFIG,
            )
        except Exception as e:
            raise APIError(f"Failed to initialize AI model: {str(e)}")

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
                
                # Initialize variables for retry logic
                max_retries = 3
                retry_count = 0
                original_response = response.text.strip().strip('`')
                
                while True:
                    try:
                        # Try to parse and validate commit message
                        commit_message = CommitMessage.parse(response.text.strip().strip('`'))
                        break  # If successful
                    except ValueError as e:
                        if "Title length" in str(e) and retry_count < max_retries:
                            retry_count += 1
                            self.console.print(f"[yellow]Title too long. Attempting to generate a shorter title (attempt {retry_count}/{max_retries})...[/yellow]")
                            
                            # Create a more specific prompt for shorter title
                            retry_prompt = f"{prompt}\n\nIMPORTANT: Previous title was too long. Please generate a new commit message with these requirements:\n"
                            retry_prompt += f"1. Title MUST be shorter than {Config.MAX_TITLE_LENGTH} characters\n"
                            retry_prompt += "2. Keep the same commit type\n"
                            retry_prompt += "3. Maintain the core meaning but be more concise\n"
                            retry_prompt += "4. Focus on the most important aspect of the change"
                            
                            response = chat_session.send_message(retry_prompt)
                            if not response or not response.text:
                                raise Exception("No response received from AI model during retry")
                        else:
                            # If we've exhausted retries or it's a different error, use the original response
                            self.console.print(f"[yellow]Unable to generate a shorter title after {retry_count} attempts. Using original response.[/yellow]")
                            response_text = original_response
                            parsed_msg = response_text.split('\n', 1)
                            title = parsed_msg[0]
                            desc = parsed_msg[1] if len(parsed_msg) > 1 else ""
                            
                            # Extract commit type if present, otherwise use 'chore'
                            type_part = title.split(":")[0] if ":" in title else "chore"
                            desc_part = title.split(":")[1].strip() if ":" in title else title
                            
                            # Calculate available length and truncate
                            available_length = Config.MAX_TITLE_LENGTH - len(type_part) - 2
                            truncated_desc = desc_part[:available_length].rsplit(' ', 1)[0] if ' ' in desc_part[:available_length] else desc_part[:available_length]
                            title = f"{type_part}: {truncated_desc}"
                            
                            # Add original title to description
                            original_title_note = f"Original title: {parsed_msg[0]}"
                            desc = f"{original_title_note}\n\n{desc}" if desc else original_title_note
                            
                            commit_message = CommitMessage(title, desc)
                            break
                
                # If we still have invalid commit type after retries, use a default type
                if not any(commit_message.title.startswith(t + ":") for t in Config.COMMIT_TYPES):
                    original_desc = commit_message.title
                    commit_message.title = f"chore: {original_desc[:Config.MAX_TITLE_LENGTH-6]}"
                    self.console.print("[yellow]Using default commit type 'chore'[/yellow]")
                
                # If title is still too long after retries, truncate it
                if len(commit_message.title) > Config.MAX_TITLE_LENGTH:
                    type_part = commit_message.title.split(":")[0]
                    desc_part = commit_message.title.split(":")[1].strip()
                    truncated_desc = desc_part[:Config.MAX_TITLE_LENGTH - len(type_part) - 2]
                    commit_message.title = f"{type_part}: {truncated_desc}"
                    self.console.print(f"[yellow]Commit title automatically truncated to meet {Config.MAX_TITLE_LENGTH} character limit[/yellow]")
                    
                    # Add truncation note to description
                    if not commit_message.description:
                        commit_message.description = f"Original title: {desc_part}"
                    else:
                        commit_message.description = f"Original title: {desc_part}\n\n{commit_message.description}"
                
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
