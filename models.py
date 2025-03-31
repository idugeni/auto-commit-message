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
    """Represents a formatted commit message with enhanced structure"""
    title: str
    description: str
    footer: str = ""
    is_breaking_change: bool = False

    def __post_init__(self):
        """Format the commit message after initialization with enhanced validation"""
        self.title = self._format_title(self.title)
        self.description = self._format_description(self.description)
        self.footer = self._format_footer(self.footer)

    def _format_title(self, title: str) -> str:
        """Format the commit title with strict validation and formatting"""
        title = title.strip()
        if len(title) > Config.MAX_TITLE_LENGTH:
            title = title[:Config.MAX_TITLE_LENGTH]
        
        # Ensure title starts with valid type
        if not any(title.startswith(t + ":") for t in Config.COMMIT_TYPES):
            raise ValueError(f"Title must start with one of: {', '.join(Config.COMMIT_TYPES)}")
            
        # Ensure proper spacing after type
        if ":" in title and not title.split(":")[1].startswith(" "):
            type_part = title.split(":")[0]
            desc_part = title.split(":")[1].strip()
            title = f"{type_part}: {desc_part}"
            
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

    def _format_footer(self, footer: str) -> str:
        """Format the commit footer with proper structure"""
        if not footer:
            return ""
            
        formatted_lines = []
        for line in footer.split('\n'):
            line = line.strip()
            if line:
                if not any(line.startswith(prefix) for prefix in ["Refs:", "Closes:", "BREAKING CHANGE:"]):
                    line = f"Refs: {line}"
                formatted_lines.extend(self._wrap_line(line))
                
        return "\n".join(formatted_lines)

    def __str__(self) -> str:
        """Enhanced string representation of the commit message"""
        title = f"{self.title}{'!' if self.is_breaking_change else ''}"
        parts = [title]
        
        if self.description:
            parts.extend(["", self.description])
            
        if self.footer:
            parts.extend(["", self.footer])
            
        return "\n".join(parts)

    @classmethod
    def parse(cls, message_text: str) -> 'CommitMessage':
        """Parse a commit message text into a CommitMessage object with enhanced parsing"""
        sections = message_text.split('\n\n')
        title = sections[0].strip()
        description = ""
        footer = ""
        
        if len(sections) > 1:
            # Check if the last section looks like a footer
            if len(sections) > 2 and any(sections[-1].strip().startswith(prefix) 
                                        for prefix in ["Refs:", "Closes:", "BREAKING CHANGE:"]):
                footer = sections[-1].strip()
                description = "\n\n".join(sections[1:-1]).strip()
            else:
                description = "\n\n".join(sections[1:]).strip()
        
        is_breaking_change = '!' in title
        title = title.replace('!', '') if is_breaking_change else title
        
        return cls(title, description, is_breaking_change)
