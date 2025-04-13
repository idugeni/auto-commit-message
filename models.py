# File: auto-commit-message/models.py

from enum import Enum
from dataclasses import dataclass, field
import re
import textwrap
from config import Config  # Ensure that config.py is importable

# Cache configuration for performance and clarity
COMMIT_TYPES = Config.COMMIT_TYPES
COMMIT_SCOPE_PATTERN = Config.COMMIT_SCOPE_PATTERN
MAX_TITLE_LENGTH = Config.MAX_TITLE_LENGTH
MAX_COMMIT_BODY_LENGTH = Config.MAX_COMMIT_BODY_LENGTH

# Precompile frequently used regex patterns
HEADER_WITH_SCOPE_REGEX = re.compile(r"^([a-z]+)\((.+)\)$")
LIST_ITEM_REGEX = re.compile(r'^([-*•]|\d+\.|[a-zA-Z]\.)\s+(.+)$')

class CommitMessageError(Exception):
    """Custom exception for commit message validation errors."""
    pass

class CommitType(Enum):
    """Enumeration of valid commit types following Conventional Commits."""
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"
    DOCS = "docs"
    FEAT = "feat"
    FIX = "fix"
    PERF = "perf"
    REFACTOR = "refactor"
    REVERT = "revert"
    STYLE = "style"
    TEST = "test"
    SECURITY = "security"

@dataclass
class CommitMessage:
    """
    Represents a formatted commit message with structured sections.
    Validation and primary formatting occur during parsing.
    """
    title: str
    description: str = field(default="")
    footer: str = field(default="")
    is_breaking_change: bool = field(init=False, default=False)

    @staticmethod
    def _validate_and_format_title(raw_title: str) -> tuple[str, bool]:
        """
        Validates the raw title against Conventional Commit rules and formats it.
        Ensures the title is not truncated and maintains readability.
        
        Args:
            raw_title (str): The raw commit title.
        
        Returns:
            tuple[str, bool]: The validated and formatted title, and a flag indicating a breaking change.
        
        Raises:
            CommitMessageError: If the title format is invalid.
        """
        title = raw_title.strip()
        if ":" not in title:
            raise CommitMessageError("Validation error: Title must include ':' to separate type and description.")

        parts = title.split(":", 1)
        header = parts[0].strip()    # Contains type, optional scope, optional '!'
        description = parts[1].strip()
        if not description:
            raise CommitMessageError("Validation error: Description after ':' cannot be empty.")

        # Capitalize the first letter of the description if necessary
        if description[0].islower():
            description = description[0].upper() + description[1:]

        # Check for breaking change marker '!' before the colon
        is_breaking = False
        if header.endswith("!"):
            is_breaking = True
            header = header[:-1].strip()
            if not header:
                raise CommitMessageError("Validation error: '!' for breaking change cannot be the only character before ':'")

        # Parse type and scope
        type_part = header
        scope_part = None
        match = HEADER_WITH_SCOPE_REGEX.match(header)
        if match:
            type_part = match.group(1)
            scope_part = match.group(2)
            if not scope_part:
                raise CommitMessageError("Validation error: Scope cannot be empty when using parentheses.")
            if not re.fullmatch(COMMIT_SCOPE_PATTERN, scope_part):
                raise CommitMessageError(
                    f"Validation error: Scope '({scope_part})' contains invalid characters. Allowed pattern: {COMMIT_SCOPE_PATTERN}"
                )
        elif '(' in header or ')' in header:
            raise CommitMessageError("Validation error: Invalid scope format. Use 'type(scope)' or just 'type'.")

        # Validate type
        if type_part not in COMMIT_TYPES:
            if type_part.lower() in COMMIT_TYPES:
                raise CommitMessageError(f"Validation error: Type '{type_part}' must be in lowercase. Did you mean '{type_part.lower()}'?")
            else:
                allowed = ', '.join(COMMIT_TYPES)
                raise CommitMessageError(f"Validation error: Type '{type_part}' is not valid. It must be one of: {allowed}")

        # Reconstruct header (include '!' if breaking change)
        final_header = type_part
        if scope_part:
            final_header += f"({scope_part})"
        if is_breaking:
            final_header += "!"

        # Remove trailing period from the description (unless it is ellipsis '...')
        if description.endswith('.') and not description.endswith('...'):
            description = description[:-1]
        # Ensure proper capitalization of description
        if description[0].islower():
            description = description[0].upper() + description[1:]

        final_title = f"{final_header}: {description}"

        # Check title length and raise error if too long
        if len(final_title) > MAX_TITLE_LENGTH:
            raise CommitMessageError(f"Validation error: Title length ({len(final_title)}) exceeds maximum allowed length ({MAX_TITLE_LENGTH}). Please provide a shorter description.")


        return final_title, is_breaking

    @staticmethod
    def _format_description(text_block: str) -> str:
        """
        Formats the commit description while preserving details and paragraph structure.

        Args:
            text_block (str): The description block text.

        Returns:
            str: The formatted description.
        """
        if not text_block:
            return ""
        # Normalize newlines and remove excessive blank lines
        text_block = re.sub(r'\n{3,}', '\n\n', text_block.strip())
        paragraphs = text_block.split('\n\n')
        wrapped_paragraphs = []

        for paragraph in paragraphs:
            lines = paragraph.strip().split('\n')
            wrapped_lines = []
            for line in lines:
                list_match = LIST_ITEM_REGEX.match(line)
                if list_match:
                    marker = list_match.group(1)
                    content = list_match.group(2)
                    indent = ' ' * (len(marker) + 1)
                    wrap_width = MAX_COMMIT_BODY_LENGTH - len(indent)
                    wrapped = textwrap.wrap(
                        content,
                        width=wrap_width,
                        replace_whitespace=False,
                        drop_whitespace=True,
                        break_long_words=False,
                        break_on_hyphens=True,
                        expand_tabs=True,
                        initial_indent='',
                        subsequent_indent=indent
                    )
                    if wrapped:
                        wrapped_lines.append(f"{marker} {wrapped[0]}")
                        wrapped_lines.extend(indent + line for line in wrapped[1:])
                else:
                    wrapped = textwrap.wrap(
                        line,
                        width=MAX_COMMIT_BODY_LENGTH,
                        replace_whitespace=False,
                        drop_whitespace=True,
                        break_long_words=False,
                        break_on_hyphens=True,
                        expand_tabs=True,
                        initial_indent='',
                        subsequent_indent=''
                    )
                    if not wrapped and line.strip():
                        wrapped = [line.strip()]
                    wrapped_lines.extend(wrapped)
            if wrapped_lines:
                wrapped_paragraphs.append('\n'.join(wrapped_lines))
        return '\n\n'.join(wrapped_paragraphs)

    @staticmethod
    def _format_footer(text_block: str) -> str:
        """
        Formats the commit footer to generate a concise summary without list markers.
        
        Args:
            text_block (str): The footer text block.

        Returns:
            str: The formatted footer as a compact summary.
        """
        if not text_block:
            return ""
        paragraphs = text_block.strip().split('\n\n')
        summary_parts = []
        for p in paragraphs:
            lines = p.strip().split('\n')
            # Remove bullet points and numbering from each line
            cleaned_lines = [re.sub(r'^[-*•]\s+|^\d+\.\s+|^[a-zA-Z]\.\s+', '', line.strip()) for line in lines]
            first_line = next((line for line in cleaned_lines if line), '')
            if first_line:
                summary_parts.append(first_line)
        return '; '.join(summary_parts)

    @classmethod
    def parse(cls, message: str) -> 'CommitMessage':
        """
        Parses a raw commit message string, validates the title, formats the
        description and footer, and returns a CommitMessage instance.

        Args:
            message (str): The raw commit message.

        Returns:
            CommitMessage: The formatted commit message instance.

        Raises:
            CommitMessageError: If the commit message format is invalid.
        """
        if not message:
            raise CommitMessageError("Validation error: Commit message cannot be empty.")

        # Split into title, description, and footer
        parts = message.strip().split('\n\n', 2)
        raw_title = parts[0]

        try:
            validated_title, is_breaking = cls._validate_and_format_title(raw_title)
        except CommitMessageError as e:
            raise CommitMessageError(f"Title validation failed: {e}") from e

        raw_description = parts[1].strip() if len(parts) > 1 else ""
        raw_footer = parts[2].strip() if len(parts) > 2 else ""

        formatted_description = cls._format_description(raw_description)
        formatted_footer = cls._format_footer(raw_footer)

        instance = cls(
            title=validated_title,
            description=formatted_description,
            footer=formatted_footer
        )
        instance.is_breaking_change = is_breaking

        return instance

    def __str__(self) -> str:
        """
        Reconstructs and returns the final formatted commit message.
        Ensures proper formatting and line wrapping for all sections.
        Includes an opening paragraph in description and properly displays footer.
        
        Returns:
            str: The commit message with proper section separation and formatting.
        """
        parts = []
        
        # Add title (already validated and formatted)
        parts.append(self.title)
        
        # Add description with opening paragraph if present
        if self.description:
            parts.append('')  # Add blank line after title
            description_parts = self.description.split('\n\n', 1)
            
            # If description doesn't start with a list item, treat first paragraph as opening
            if not LIST_ITEM_REGEX.match(description_parts[0]):
                parts.append(self._format_description(description_parts[0]))
                if len(description_parts) > 1:
                    parts.append('')  # Add spacing before list items
                    parts.append(self._format_description(description_parts[1]))
            else:
                # If no opening paragraph, just add the description as is
                parts.append(self._format_description(self.description))
        
        # Add footer with proper formatting
        if self.footer:
            parts.append('')  # Ensure blank line before footer
            parts.append(self._format_description(self.footer))
        
        return '\n'.join(parts)
