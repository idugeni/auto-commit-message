# File: auto-commit-message/models.py

from enum import Enum
from dataclasses import dataclass, field
import re
import textwrap
from config import Config  # Ensure config.py is importable

class CommitType(Enum):
    """Valid commit types enumeration"""
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
    Represents a formatted commit message with an enhanced structure.
    Validation and primary formatting occur during the parsing process.
    """
    title: str
    description: str = field(default="")
    footer: str = field(default="")
    # is_breaking_change is set during parsing, not initial initialization
    is_breaking_change: bool = field(init=False, default=False)

    @staticmethod
    def _validate_and_format_title(raw_title: str) -> tuple[str, bool]:
        """
        Validates the raw title against Conventional Commit rules and formats it.
        Returns the validated title and a boolean indicating if it's a breaking change.
        Raises ValueError on validation failure.
        """
        title = raw_title.strip()

        # 1. Basic Format Check: must contain ':' and a description part
        if ":" not in title:
            raise ValueError("Title must contain ':' to separate type and description.")
        
        parts = title.split(":", 1)
        header = parts[0].strip()  # Contains type, optional scope, optional '!'
        description = parts[1].strip()
        
        if not description:
            raise ValueError("Description part after ':' cannot be empty.")
        
        # Capitalize first letter of description if it's not already
        if description[0].islower():
            description = description[0].upper() + description[1:]

        # 2. Check Breaking Change Marker '!': must be right before ':'
        is_breaking = False
        if header.endswith("!"):
            is_breaking = True
            # Remove '!' for further parsing, ensure header isn't empty afterward
            header = header[:-1].strip()
            if not header:
                raise ValueError("Invalid title format: Breaking change '!' cannot be the only character before ':'")

        # 3. Parse Type and Scope
        type_part = header
        scope_part = None
        # Match 'type(scope)' format using simple regex
        match = re.match(r"^([a-z]+)\((.+)\)$", header)
        if match:
            type_part = match.group(1)
            scope_part = match.group(2)
            # Validate scope content
            if not scope_part:
                raise ValueError("Scope cannot be empty when parentheses are present.")
            if not re.fullmatch(Config.COMMIT_SCOPE_PATTERN, scope_part):
                raise ValueError(f"Scope '({scope_part})' contains invalid characters. Allowed pattern: {Config.COMMIT_SCOPE_PATTERN}")
        elif '(' in header or ')' in header:
            # If parentheses exist but don't match the 'type(scope)' regex
            raise ValueError("Invalid scope format. Use 'type(scope)' or just 'type'.")
        # else: No scope, type_part is correct

        # 4. Validate Type
        if type_part not in Config.COMMIT_TYPES:
            # Provide suggestion if the issue is only case sensitivity
            if type_part.lower() in Config.COMMIT_TYPES:
                raise ValueError(f"Invalid type: '{type_part}'. Type must be lowercase. Did you mean '{type_part.lower()}'?")
            else:
                raise ValueError(f"Invalid type: '{type_part}'. Must be one of: {', '.join(Config.COMMIT_TYPES)}")

        # 5. Reconstruct Header (including '!' if breaking change)
        final_header = type_part
        if scope_part:
            final_header += f"({scope_part})"
        if is_breaking:
            final_header += "!"

        # 6. Final Title Construction and Additional Validation
        # Remove trailing period from description (unless it's ellipsis '...')
        if description.endswith('.') and not description.endswith('...'):
            description = description[:-1]
            
        # Ensure description doesn't start with lowercase after type
        if description[0].islower():
            description = description[0].upper() + description[1:]

        final_title = f"{final_header}: {description}"

        # 7. Check Title Length
        if len(final_title) > Config.MAX_TITLE_LENGTH:
            # Try to shorten description while keeping meaning
            words = description.split()
            shortened = words[0]
            for word in words[1:]:
                test_title = f"{final_header}: {shortened} {word}"
                if len(test_title) <= Config.MAX_TITLE_LENGTH:
                    shortened += f" {word}"
                else:
                    break
            if len(f"{final_header}: {shortened}") <= Config.MAX_TITLE_LENGTH:
                final_title = f"{final_header}: {shortened}"
            else:
                raise ValueError(f"Title length ({len(final_title)}) exceeds maximum limit ({Config.MAX_TITLE_LENGTH}) and cannot be shortened: '{final_title[:Config.MAX_TITLE_LENGTH]}...'")

        return final_title, is_breaking

    @staticmethod
    def _format_body_part(text_block: str, is_footer: bool = False) -> str:
        """
        Formats a block of text (description or footer) with line wrapping
        while attempting to preserve paragraph structure.
        For footer, creates a more concise summary without bullet points.
        Handles various formats including single paragraphs, bullet points,
        and multiple changes flexibly.
        """
        if not text_block:
            return ""

        # For footer, create a concise summary without bullet points
        if is_footer:
            # Split into paragraphs and clean up each paragraph
            paragraphs = text_block.strip().split('\n\n')
            summary_parts = []
            for p in paragraphs:
                # Remove bullet points and clean up the text
                lines = p.strip().split('\n')
                cleaned_lines = [re.sub(r'^[-*•]\s+|^\d+\.\s+|^[a-zA-Z]\.\s+', '', line.strip()) for line in lines]
                # Take first non-empty line after cleaning
                first_line = next((line for line in cleaned_lines if line), '')
                if first_line:
                    summary_parts.append(first_line)
            # Join with semicolons for a compact representation
            return '; '.join(summary_parts)

        # For description, preserve full detail with paragraphs
        # First, normalize line endings and remove excessive blank lines
        text_block = re.sub(r'\n{3,}', '\n\n', text_block.strip())
        paragraphs = text_block.split('\n\n')
        wrapped_paragraphs = []

        for paragraph in paragraphs:
            # Handle bullet points, numbered lists, and regular text
            lines = paragraph.strip().split('\n')
            wrapped_lines = []
            
            for line in lines:
                # Enhanced pattern matching for various list formats
                list_match = re.match(r'^([-*•]|\d+\.|[a-zA-Z]\.)\s+(.+)$', line)
                if list_match:
                    # Preserve list marker and handle content separately
                    marker = list_match.group(1)
                    content = list_match.group(2)
                    indent = ' ' * (len(marker) + 1)
                    
                    # Wrap the content part only
                    wrap_width = Config.MAX_COMMIT_BODY_LENGTH - len(indent)
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
                        # First line with marker
                        wrapped_lines.append(f"{marker} {wrapped[0]}")
                        # Subsequent lines with proper indentation
                        wrapped_lines.extend(indent + line for line in wrapped[1:])
                else:
                    # Regular paragraph text
                    wrapped = textwrap.wrap(
                        line,
                        width=Config.MAX_COMMIT_BODY_LENGTH,
                        replace_whitespace=False,
                        drop_whitespace=True,
                        break_long_words=False,
                        break_on_hyphens=True,
                        expand_tabs=True,
                        initial_indent='',
                        subsequent_indent=''
                    )
                    # Ensure we don't lose any content
                    if not wrapped and line.strip():
                        wrapped = [line.strip()]
                    wrapped_lines.extend(wrapped)
            
            # Only add non-empty paragraphs
            if wrapped_lines:
                wrapped_paragraphs.append('\n'.join(wrapped_lines))

        # Rejoin paragraphs with double newlines
        return '\n\n'.join(wrapped_paragraphs)

    @classmethod
    def parse(cls, message: str) -> 'CommitMessage':
        """
        Parses a raw commit message string, validates the title,
        formats the body/footer, and returns a CommitMessage instance.
        """
        if not message:
            raise ValueError("Cannot parse an empty commit message.")

        # Split into potential title, body, footer
        parts = message.strip().split('\n\n', 2)
        raw_title = parts[0]

        # Validate and format the title (raises ValueError on failure)
        try:
            validated_title, is_breaking = cls._validate_and_format_title(raw_title)
        except ValueError as e:
            # Add context to the title validation error
            raise ValueError(f"Title validation failed: {e}") from e

        # Extract and format body and footer
        raw_description = parts[1].strip() if len(parts) > 1 else ""
        raw_footer = parts[2].strip() if len(parts) > 2 else ""

        # Use _format_body_part for description and footer consistently
        formatted_description = cls._format_body_part(raw_description)
        formatted_footer = cls._format_body_part(raw_footer, is_footer=True)

        # Create instance
        instance = cls(
            title=validated_title,
            description=formatted_description,
            footer=formatted_footer
        )
        # Set breaking change flag based on title validation result
        instance.is_breaking_change = is_breaking

        return instance

    def __str__(self) -> str:
        """Reconstructs the formatted commit message string."""
        parts = [self.title]
        if self.description:
            # Add blank line before body
            parts.extend(['', self.description])
        if self.footer:
            # Add blank line before footer if body exists, OR if no body but footer exists
            if self.description or (not self.description and self.footer):
                parts.append('')
            parts.append(self.footer)

        # Join all parts with a single newline
        # Blank lines between sections were added explicitly above
        return '\n'.join(parts)