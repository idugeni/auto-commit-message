import google.generativeai as genai
from config import Config
from models import CommitMessage

class AIModelManager:
    """Manage AI model operations with precision and care."""
    def __init__(self, api_key: str):
        self.model = self._initialize_model(api_key)

    @staticmethod
    def _initialize_model(api_key: str) -> genai.GenerativeModel:
        """Initialize and configure the Gemini AI model."""
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            generation_config=Config.GENERATION_CONFIG,
        )

    def generate_commit_message(self, diff: str) -> CommitMessage:
        """Generate commit message using the AI model with clarity and warmth."""
        if not diff:
            return CommitMessage("chore: no changes to commit", "")

        prompt = self._create_prompt(diff)
        try:
            chat_session = self.model.start_chat(history=[])
            response = chat_session.send_message(prompt)
            return CommitMessage.parse(response.text.strip().strip('`'))
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

1. **Format:**
   - **Title:** One line, maximum 50 characters.
   - **Separation:** One blank line after the title.
   - **Description:** One or more lines, each wrapped at 72 characters.

2. **Title Requirements:**
   - Must start with one of these prefixes: {commit_types_str}
   - Be concise yet descriptive.
   - Follow the format: "<type>: <brief description>".
   - If a breaking change is introduced, append an exclamation mark (!) to the type.

3. **Description Requirements:**
   - Provide meaningful context about what and why the changes were made (avoid describing how).
   - Include relevant ticket or issue numbers, if identifiable.
   - Use imperative mood (e.g., "Add feature" instead of "Added feature").

## Output Format
<type>: <brief description>

<detailed description>

**Note:** Return ONLY the formatted commit message without any additional text, explanations, or code blocks.
"""
