from enum import Enum
from dataclasses import dataclass
import re
from config import Config

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
    """Represents a formatted commit message with enhanced structure"""
    title: str
    description: str
    footer: str = ""
    is_breaking_change: bool = False

    def _format_title(self, title: str) -> str:
        title = title.strip()
        if ":" not in title or not title.split(":", 1)[1].strip():
            raise ValueError("Title must follow format '<type>[(scope)]: <description>' and have a description")

        parts = title.split(":", 1)
        type_scope = parts[0].strip()
        description = parts[1].strip()

        has_breaking_change = False
        if type_scope.endswith("!"):
            type_scope = type_scope[:-1]
            has_breaking_change = True

        type_part = type_scope
        scope_part = None
        if type_scope.endswith(")"):
            idx_open = type_scope.find("(")
            if idx_open != -1 and idx_open < len(type_scope) - 1:
                type_part = type_scope[:idx_open]
                scope_part = type_scope[idx_open+1:-1]
                if not scope_part:
                    raise ValueError("Scope cannot be empty if parentheses are present")
                if not re.fullmatch(Config.COMMIT_SCOPE_PATTERN, scope_part):
                    raise ValueError(f"Invalid scope format '{scope_part}'")

            else:
                raise ValueError("Invalid scope format")

        else:
            if "(" in type_scope or ")" in type_scope:
                raise ValueError("Invalid scope format")

        if type_part not in Config.COMMIT_TYPES:
            raise ValueError(f"Invalid title type '{type_part}'")

        if len(title) > Config.MAX_TITLE_LENGTH:
            raise ValueError(f"Title length ({len(title)}) exceeds maximum limit ({Config.MAX_TITLE_LENGTH})")

        return f"{type_scope}: {description}"

    def _format_description(self, description: str) -> str:
        if not description:
            return description

        lines = [line.strip() for line in description.split('\n') if line.strip()]
        formatted_lines = []
        total_length = 0
        bullet_points = []

        for line in lines:
            if line.startswith('-'):
                bullet_points.append(line.strip('- ').strip())
                continue

            if bullet_points:
                for i, point in enumerate(bullet_points):
                    if total_length + len(point) + 4 > 500:
                        formatted_lines.append('...')
                        bullet_points = []
                        break
                    formatted_line = f"- {point}"
                    formatted_lines.extend(self._wrap_bullet_point(formatted_line))
                    total_length += len(formatted_line) + 1
                bullet_points = []

            if total_length + len(line) + 2 > 500:
                if not any(l.endswith('...') for l in formatted_lines):
                    formatted_lines.append('...')
                break

            formatted_lines.extend(self._wrap_text(line))
            total_length += len(line) + 1

        if bullet_points:
            for i, point in enumerate(bullet_points):
                if total_length + len(point) + 4 > 500:
                    formatted_lines.append('...')
                    break
                formatted_line = f"- {point}"
                formatted_lines.extend(self._wrap_bullet_point(formatted_line))
                total_length += len(formatted_line) + 1

        return '\n'.join(formatted_lines)

    def _wrap_text(self, line: str, is_bullet: bool = False) -> list[str]:
        if len(line) <= Config.MAX_COMMIT_BODY_LENGTH:
            return [line]

        lines = []
        current_line = line

        while len(current_line) > Config.MAX_COMMIT_BODY_LENGTH:
            split_index = current_line[:Config.MAX_COMMIT_BODY_LENGTH].rfind(' ')
            if split_index == -1:
                split_index = Config.MAX_COMMIT_BODY_LENGTH

            lines.append(current_line[:split_index].rstrip())
            continuation_indent = "  " if is_bullet else ""
            current_line = continuation_indent + current_line[split_index:].lstrip()

        if current_line:
            lines.append(current_line)

        return lines

    def _wrap_bullet_point(self, line: str) -> list[str]:
        return self._wrap_text(line, is_bullet=True)

    def _format_footer(self, footer: str) -> str:
        if not footer:
            return footer

        footer_lines = [line.strip() for line in footer.split('\n') if line.strip()]
        formatted_lines = []

        for line in footer_lines:
            if any(line.startswith(prefix) for prefix in ['Refs:', 'Closes:', 'BREAKING CHANGE:']):
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @classmethod
    def parse(cls, message: str) -> 'CommitMessage':
        if not message:
            raise ValueError("Cannot parse an empty commit message")

        parts = message.strip().split('\n\n', 2)
        raw_title = parts[0].strip()
        validated_title = cls._format_title(None, raw_title)

        description = parts[1].strip() if len(parts) > 1 else ""
        footer = parts[2].strip() if len(parts) > 2 else ""

        instance = cls(title=validated_title, description=description, footer=footer)
        instance.description = instance._format_description(instance.description)
        instance.footer = instance._format_footer(instance.footer)
        instance.is_breaking_change = '!' in validated_title.split(':')[0]

        return instance

    def __str__(self) -> str:
        parts = [self.title]
        if self.description:
            parts.append(self.description)
        if self.footer:
            parts.append(self.footer)
        return '\n\n'.join(parts)
