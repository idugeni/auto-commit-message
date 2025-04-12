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
            self.console.print("[yellow]No changes detected, using default commit message[/yellow]")
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

                progress.update(task, advance=20)
                chat_session = self.model.start_chat(history=[])
                progress.update(task, advance=20)

                max_retries = 3
                retry_count = 0
                last_error = None
                generated_text = None

                while retry_count <= max_retries:
                    current_prompt = prompt
                    if retry_count > 0 and last_error:
                        # Create specific retry prompt
                        self.console.print(f"[yellow]Attempt {retry_count}/{max_retries}: Retrying due to error: {last_error}[/yellow]")
                        retry_prompt_detail = f"The previous attempt failed with the error: '{last_error}'.\n"
                        if "Title must start with one of" in str(last_error):
                             retry_prompt_detail += f"Ensure the commit type is one of: {', '.join(Config.COMMIT_TYPES)}.\n"
                        elif "Title length" in str(last_error):
                             retry_prompt_detail += f"The title was too long. It MUST be under {Config.MAX_TITLE_LENGTH} characters.\n"
                        elif "Title must follow format" in str(last_error):
                             retry_prompt_detail += "Ensure the title format is exactly '<type>: <description>'.\n"
                        else:
                             retry_prompt_detail += "Please strictly follow all formatting rules mentioned in the requirements.\n"

                        current_prompt = f"""
# Previous Attempt Review

The previous attempt to generate a commit message resulted in the following error:
`{last_error}`

The generated message was:
{generated_text}


# Correction Task

Please regenerate the commit message based on the original Git Diff, paying close attention to the formatting requirements, especially the one mentioned in the error.

## Original Requirements Reminder (Summary)
- Format: `<type>[(scope)]: <description>` (Title) + Optional Body + Optional Footer
- Title: STRICTLY under {Config.MAX_TITLE_LENGTH} chars, imperative mood, starts with a valid type ({', '.join(Config.COMMIT_TYPES)})
- Scope: Optional, must match pattern {Config.COMMIT_SCOPE_PATTERN} (lowercase letters, numbers, hyphens)
- Body: Wrap at {Config.MAX_COMMIT_BODY_LENGTH} chars, explain WHAT and WHY.
- Footer: Use prefixes like `Refs:`, `Closes:`, `BREAKING CHANGE:`.

## Original Input: Git Diff
```diff
{diff}
```
Output Format
Return ONLY the corrected commit message.
"""
                    import time
                    time.sleep(1 * retry_count) # Backoff

                    try:
                        progress.update(task, advance=int(15 / (max_retries + 1))) # Update progress per attempt
                        response = chat_session.send_message(current_prompt)
                        progress.update(task, advance=int(15 / (max_retries + 1)))

                        if not response or not response.text:
                            last_error = "Received empty response from AI model"
                            generated_text = ""
                            retry_count += 1
                            continue

                        generated_text = response.text.strip().strip('`')

                        # Try to parse and validate using CommitMessage
                        commit_message = CommitMessage.parse(generated_text)
                        # If successful, exit the loop
                        self.console.print("[green]✓ Commit message format validated successfully.[/green]")
                        last_error = None # Reset error on success
                        break # Exit retry loop

                    except ValueError as e:
                        # Handle validation errors
                        last_error = str(e)
                        retry_count += 1
                        progress.update(task, advance=int(10 / (max_retries + 1)))
                    except Exception as e:
                        # Handle communication errors
                        self.console.print(f"[red]Error during AI communication attempt {retry_count}: {str(e)}[/red]")
                        if retry_count >= max_retries:
                           raise Exception(f"Failed to generate commit message after multiple retries: {str(e)}") from e
                        last_error = f"AI communication error: {str(e)}"
                        retry_count += 1


                progress.update(task, advance=10) # Final progress update

                # --- Fallback Logic ---
                if last_error:
                    self.console.print(f"[bold yellow]Warning:[/bold yellow] AI failed to generate a perfectly formatted message after {max_retries} retries (Last error: {last_error}). Applying automatic corrections...")
                    # Use the last generated text as base
                    raw_message = generated_text if generated_text else "chore: fallback due to generation failure"
                    parts = raw_message.split('\n\n', 2)
                    title = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ""
                    footer = parts[2].strip() if len(parts) > 2 else ""
                    original_title = title # Store original title for reference

                    # 1. Try to fix Type and Scope
                    type_scope = title.split(':')[0]
                    desc_part = title.split(':', 1)[1].strip() if ':' in title else title

                    # Extract type, scope, and breaking change marker
                    type_part = type_scope
                    scope_part = None
                    has_breaking_change = False

                    # Handle breaking change marker
                    if '!' in type_scope:
                        type_scope_parts = type_scope.split('!', 1)
                        type_part = type_scope_parts[0]
                        has_breaking_change = True
                        remaining = type_scope_parts[1]
                    else:
                        remaining = type_scope

                    # Handle scope
                    if '(' in remaining:
                        if remaining.endswith(')'):
                            type_scope_parts = remaining.split('(', 1)
                            type_part = type_part or type_scope_parts[0]
                            scope_part = type_scope_parts[1][:-1]  # Remove closing ')'
                            
                            # Validate and fix scope if needed
                            if not re.match(Config.COMMIT_SCOPE_PATTERN, scope_part):
                                self.console.print(f"[yellow]Fallback: Removing invalid scope '({scope_part})'.[/yellow]")
                                scope_part = None
                        else:
                            self.console.print("[yellow]Fallback: Removing malformed scope (missing closing parenthesis).[/yellow]")

                    # Fix type if invalid
                    if type_part not in Config.COMMIT_TYPES:
                        self.console.print(f"[yellow]Fallback: Correcting invalid type '{type_part}' to 'chore'.[/yellow]")
                        type_part = "chore"
                        # If no ':', description is the entire title
                        if ':' not in title:
                            desc_part = title

                    # 2. Ensure space after ':'
                    if not desc_part.startswith(" ") and ':' in title :
                        desc_part = desc_part.lstrip() # Remove leading spaces if any

                    # 3. Try to fix Title Length
                    max_desc_len = Config.MAX_TITLE_LENGTH - len(type_part) - 2 # Account for ':' and space
                    if len(desc_part) > max_desc_len:
                        self.console.print(f"[yellow]Fallback: Truncating title description to fit {Config.MAX_TITLE_LENGTH} chars.[/yellow]")
                        # Try to cut at last space
                        truncated_desc = desc_part[:max_desc_len].rsplit(' ', 1)[0] if ' ' in desc_part[:max_desc_len] else desc_part[:max_desc_len]
                        desc_part = truncated_desc

                    # 4. Reconstruct Title
                    title_parts = [type_part]
                    if scope_part:
                        title_parts.append(f"({scope_part})")
                    if has_breaking_change:
                        title_parts.append("!")
                    title = f"{''.join(title_parts)}: {desc_part}".rstrip('.!?') # Remove trailing punctuation

                    # 5. Add notes to description if there are modifications
                    correction_notes = []
                    if title != original_title:
                         correction_notes.append(f"Original AI title: {original_title}")
                    if correction_notes:
                         description = "\n\n".join(correction_notes) + (f"\n\n{description}" if description else "")

                    # Create CommitMessage object manually to bypass post_init validation
                    # since we have already tried to fix it here.
                    # We don't call parse again.
                    commit_message = CommitMessage(title=title, description=description, footer=footer)
                    # Reformat description and footer after fallback
                    commit_message.description = commit_message._format_description(commit_message.description)
                    commit_message.footer = commit_message._format_footer(commit_message.footer)


                # --- End Fallback Logic ---


                # Display the generated message
                self.console.print(Panel(
                    f"[bold green]Title:[/bold green] {commit_message.title}\n\n" +
                    (f"[bold green]Description:[/bold green]\n{commit_message.description}\n\n" if commit_message.description else "") +
                    (f"[bold green]Footer:[/bold green]\n{commit_message.footer}" if commit_message.footer else ""),
                    title="[bold]Generated Commit Message[/bold]",
                    border_style="green"
                ))

                progress.update(task, completed=100)
                return commit_message
        except TimeoutError:
            raise Exception("AI model response timed out. Please try again.")
        except Exception as e:
            # Handle other errors that may occur outside the retry loop
            self.console.print(f"[bold red]An unexpected error occurred: {str(e)}[/bold red]")
            raise Exception(f"Failed to generate commit message: {str(e)}") from e

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
   - Follow format: "<type>[(scope)]: <brief description>"
   - Scope is optional, must be lowercase letters, numbers, or hyphens only
   - STRICT Maximum 50 characters - be concise and direct
   - Focus on the core change, avoid unnecessary words
   - Use imperative mood (e.g., "add" not "added")
   - If breaking change, append "!" after type/scope
   - Examples:
     * "feat(auth): add JWT support" (with scope)
     * "feat: add user authentication" (without scope)
     * "feat(api)!: change auth endpoint" (breaking change)

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
