from enum import Enum
from dataclasses import dataclass
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
    """Represents a formatted commit message"""
    title: str
    description: str
    is_breaking_change: bool = False

    def __post_init__(self):
        """Format the commit message after initialization"""
        self.title = self._format_title(self.title)
        self.description = self._format_description(self.description)

    def _format_title(self, title: str) -> str:
        """Format the commit title without applying length restrictions"""
        return title

    def _format_description(self, description: str) -> str:
        """Format the commit description with proper line wrapping"""
        if not description:
            return description

        formatted_lines = []
        for line in description.split('\n'):
            if not line.strip():
                formatted_lines.append('')
                continue

            if line.strip().startswith('-'):
                formatted_lines.extend(
                    self._wrap_bullet_point(line.strip())
                )
            else:
                formatted_lines.extend(
                    self._wrap_line(line)
                )

        return '\n'.join(formatted_lines)

    def _wrap_bullet_point(self, line: str) -> list[str]:
        """Wrap a bullet point line at the maximum length"""
        lines = []
        current_line = line

        while len(current_line) > Config.MAX_COMMIT_BODY_LENGTH:
            split_point = current_line[:Config.MAX_COMMIT_BODY_LENGTH].rfind(' ')
            if split_point == -1:
                split_point = Config.MAX_COMMIT_BODY_LENGTH

            lines.append(current_line[:split_point])
            current_line = "  " + current_line[split_point:].strip()

        lines.append(current_line)
        return lines

    def _wrap_line(self, line: str) -> list[str]:
        """Wrap a regular line at the maximum length"""
        lines = []
        while len(line) > Config.MAX_COMMIT_BODY_LENGTH:
            split_point = line[:Config.MAX_COMMIT_BODY_LENGTH].rfind(' ')
            if split_point == -1:
                split_point = Config.MAX_COMMIT_BODY_LENGTH

            lines.append(line[:split_point])
            line = line[split_point:].strip()

        if line:
            lines.append(line)
        return lines

    def __str__(self) -> str:
        """String representation of the commit message"""
        title = f"{self.title}{'!' if self.is_breaking_change else ''}"
        return f"{title}\n\n{self.description}" if self.description else title

    @classmethod
    def parse(cls, message_text: str) -> 'CommitMessage':
        """Parse a commit message text into a CommitMessage object"""
        parts = message_text.split('\n\n', 1)
        title = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
        
        is_breaking_change = '!' in title
        title = title.replace('!', '') if is_breaking_change else title
        
        return cls(title, description, is_breaking_change)
