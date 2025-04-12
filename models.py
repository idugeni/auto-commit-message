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
        """Format AND validate the commit title according to Conventional Commits."""
        title = title.strip()

        # 1. Basic Format Check
        if ":" not in title or not title.split(":", 1)[1].strip():
            raise ValueError("Title must follow format '<type>[(scope)]: <description>' and have a description.")

        parts = title.split(":", 1)
        type_scope = parts[0].strip()
        description = parts[1].strip()

        # Extract breaking change marker
        has_breaking_change = False
        type_scope_for_parse = type_scope
        if type_scope_for_parse.endswith("!"):
            type_scope_for_parse = type_scope_for_parse[:-1]
            has_breaking_change = True

        # Extract scope jika ada (opsional, hanya jika format benar)
        type_part = type_scope_for_parse
        scope_part = None
        if type_scope_for_parse.endswith(")"):
            idx_open = type_scope_for_parse.find("(")
            # Pastikan tanda kurung pembuka terdapat sebelum kurung tutup
            if idx_open != -1 and idx_open < len(type_scope_for_parse) - 1:
                type_part = type_scope_for_parse[:idx_open]
                scope_part = type_scope_for_parse[idx_open+1:-1]
                if not scope_part:
                    raise ValueError("Scope tidak boleh kosong jika tanda kurung ada.")
                if not re.fullmatch(Config.COMMIT_SCOPE_PATTERN, scope_part):
                    raise ValueError(f"Format scope tidak valid '{scope_part}'. Gunakan huruf kecil, angka, dan tanda minus saja.")
            else:
                # Kurung tutup tanpa kurung buka di posisi benar dianggap salah format
                raise ValueError("Format scope salah. Jika ada scope harus dalam tanda kurung persis setelah type dan diakhiri kurung tutup.")
        else:
            # Tidak boleh ada kurung buka/tutup di tempat lain
            if "(" in type_scope_for_parse or ")" in type_scope_for_parse:
                raise ValueError("Format scope salah. Scope opsional, tapi jika ada harus seperti 'type(scope)': ...")

        # Validasi Type
        if type_part not in Config.COMMIT_TYPES:
            raise ValueError(f"Tipe pada judul '{type_part}' tidak valid. Harus salah satu dari: {', '.join(Config.COMMIT_TYPES)}")

        # Validasi Scope (jika ada, sudah divalidasi regex saat parsing)

        # Cek panjang
        if len(title) > Config.MAX_TITLE_LENGTH:
            raise ValueError(f"Panjang judul ({len(title)}) melebihi batas maksimum ({Config.MAX_TITLE_LENGTH}).")

        # Cek titik di akhir deskripsi
        if description.endswith('.'):
            # Boleh elipsis (...), bukan titik tunggal
            if not description.endswith('...'):
                title = title.rstrip('.')

        return title

    def _format_description(self, description: str) -> str:
        """Format the commit description with proper line wrapping, length limit, and punctuation"""
        if not description:
            return description

        # Split into lines and process each line
        lines = [line.strip() for line in description.split('\n') if line.strip()]
        formatted_lines = []
        total_length = 0
        bullet_points = []

        for line in lines:
            # Collect bullet points separately
            if line.startswith('-'):
                bullet_points.append(line.strip('- ').strip())
                continue

            # Process non-bullet point lines
            if bullet_points:
                # Format and add collected bullet points before continuing
                for i, point in enumerate(bullet_points):
                    if total_length + len(point) + 4 > 500:  # Account for "- " and potential punctuation
                        formatted_lines.append('...')
                        bullet_points = []
                        break
                    formatted_line = f"- {point}{'.' if i == len(bullet_points)-1 else ','}"
                    formatted_lines.extend(self._wrap_bullet_point(formatted_line))
                    total_length += len(formatted_line) + 1  # +1 for newline
                bullet_points = []
                formatted_lines.append('')  # Add spacing after bullet points

            # Process regular line
            if total_length + len(line) + 2 > 500:  # +2 for potential punctuation and newline
                if not any(l.endswith('...') for l in formatted_lines):
                    formatted_lines.append('...')
                break
            
            if not line.endswith(('.', '!', '?')):
                line = f"{line}."
            formatted_lines.extend(self._wrap_text(line))
            total_length += len(line) + 1  # +1 for newline
            formatted_lines.append('')  # Add blank line between paragraphs

        # Process any remaining bullet points
        if bullet_points:
            for i, point in enumerate(bullet_points):
                if total_length + len(point) + 4 > 500:
                    formatted_lines.append('...')
                    break
                formatted_line = f"- {point}{'.' if i == len(bullet_points)-1 else ','}"
                formatted_lines.extend(self._wrap_bullet_point(formatted_line))
                total_length += len(formatted_line) + 1

        # Clean up empty lines
        while formatted_lines and not formatted_lines[-1]:
            formatted_lines.pop()

        return '\n'.join(formatted_lines)

    def _wrap_text(self, line: str, is_bullet: bool = False) -> list[str]:
        """Wrap a line of text at the maximum length with proper indentation
        
        Args:
            line: The text line to wrap
            is_bullet: Whether the line is a bullet point (adds indentation)
        """
        if len(line) <= Config.MAX_COMMIT_BODY_LENGTH:
            return [line]
            
        lines = []
        current_line = line
        
        while len(current_line) > Config.MAX_COMMIT_BODY_LENGTH:
            split_index = current_line[:Config.MAX_COMMIT_BODY_LENGTH].rfind(' ')
            if split_index == -1:
                split_index = Config.MAX_COMMIT_BODY_LENGTH
            
            lines.append(current_line[:split_index].rstrip())
            
            # Add indentation for bullet point continuation lines
            continuation_indent = "  " if is_bullet else ""
            current_line = continuation_indent + current_line[split_index:].lstrip()
        
        if current_line:
            lines.append(current_line)
            
        return lines

    def _wrap_bullet_point(self, line: str) -> list[str]:
        """Wrap a bullet point line with proper formatting and indentation
        
        Args:
            line: The bullet point line to wrap
        """
        return self._wrap_text(line, is_bullet=True)

    def _format_footer(self, footer: str) -> str:
        """Format the commit footer with proper structure and validation"""
        if not footer:
            return footer

        footer_lines = [line.strip() for line in footer.split('\n') if line.strip()]
        formatted_lines = []

        for line in footer_lines:
            # Validate and format footer references
            if any(line.startswith(prefix) for prefix in ['Refs:', 'Closes:', 'BREAKING CHANGE:']):
                if not line.endswith('.'):
                    line += '.'
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @classmethod
    def parse(cls, message: str) -> 'CommitMessage':
        """Parse a commit message string and VALIDATE the title."""
        if not message:
            raise ValueError("Cannot parse an empty commit message.")

        parts = message.strip().split('\n\n', 2)
        raw_title = parts[0].strip()

        # *** Call validation within parse ***
        validated_title = cls._format_title(None, raw_title) # Pass None for self

        description = parts[1].strip() if len(parts) > 1 else ""
        footer = parts[2].strip() if len(parts) > 2 else ""

        # Format description and footer *after* successful parsing
        instance = cls(title=validated_title, description=description, footer=footer)
        instance.description = instance._format_description(instance.description)
        instance.footer = instance._format_footer(instance.footer)

        # Check for breaking change marker (can be done here or in __init__)
        instance.is_breaking_change = '!' in validated_title.split(':')[0]

        return instance

    def __str__(self) -> str:
        """Convert the commit message to a properly formatted string"""
        parts = [self.title]
        
        if self.description:
            parts.extend(['', self.description])
            
        if self.footer:
            parts.extend(['', self.footer])
            
        return '\n'.join(parts)
