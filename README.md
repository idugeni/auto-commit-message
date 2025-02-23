# Auto Commit Message

<p align="center">
  <img src="https://opengraph.githubassets.com/856c5388bec324b86d5fb9acf0cc386418284ea1/idugeni/auto-commit-message" alt="Auto Commit Message" width="600">
</p>

<p align="center">
  <strong>Automated Conventional Commit Message Generation Powered by Google Gemini AI</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#commit-types">Commit Types</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## Overview

<p align="center">
  <a href="https://www.youtube.com/watch?v=lbaSAhxPpWY">
    <img src="https://img.youtube.com/vi/lbaSAhxPpWY/maxresdefault.jpg" alt="Git Commit Like a Pro! Use Gemini AI to Automate Perfect Messages!" width="600">
  </a>
</p>

Auto Commit Message is a sophisticated tool designed to elevate your Git workflow through AI-powered commit message generation. By leveraging Google Gemini's advanced language model, this application analyzes repository changes to produce precise, standardized commit messages that follow best practices.

This tool bridges the gap between rapid development and comprehensive documentation by ensuring each commit message maintains a professional standard regardless of project complexity or team size.

## Key Features

- **Intelligent Change Analysis**: Automatically detects and interprets staged changes in your Git repository
- **AI-Powered Messaging**: Utilizes Google Gemini API to generate contextually accurate commit messages
- **Conventional Commit Compliance**: Ensures all generated messages adhere to the Conventional Commits specification
- **Repository Validation**: Verifies working directory is a valid Git repository before execution
- **Centralized Configuration**: Maintains global settings for consistent use across multiple projects
- **Git Command Integration**: Seamlessly integrates with Git via custom alias for frictionless workflow
- **Error Handling**: Robust error detection and reporting with clear guidance for resolution
- **Cross-Platform Support**: Compatible with Windows environments with planned expansion to macOS and Linux

## Installation

### Prerequisites

- Python 3.7 or higher
- Git version 2.20 or higher
- Google Gemini API key

### Step-by-Step Installation

1. **Verify Python Installation**

   ```sh
   python --version
   ```

   *If not available, download and install from [python.org](https://www.python.org/)*

2. **Clone the Repository**

   ```sh
   git clone https://github.com/idugeni/auto-commit-message.git
   cd auto-commit-message
   ```

3. **Execute Setup Script**

   ```sh
   setup.bat
   ```

   This creates the necessary directory structure at `C:\Tools\auto-commit-message\` and copies required files.

4. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

   *run the command in folder `C:\Tools\auto-commit-message\`*

   or

   ```bash
   pip install google-generativeai
   pip install python-dotenv
   ```

5. **Configure API Access**

   Create `.env.local` in `C:\Tools\auto-commit-message\` with your Google Gemini API key:

   ```sh
   GEMINI_API_KEY=your_api_key_here
   ```

6. **Configure Git Alias**

   This document provides instructions on how to configure a Git alias for the `auto-commit-message` script.  Two options are provided: one for all users (system-wide) and one for a specific user.

   - ***System-Wide Alias (All Users)***

   This configuration applies to all users on the system.  It requires administrator privileges.

   ```sh
   git config --system alias.acm '!C:/Program Files/Python313/python.exe C:/Tools/auto-commit-message/main.py' --replace-all
   ```

   *Note: This assumes Python is installed in the system-wide location `(e.g., C:/Program Files/Python313)`. Adjust the Python path if necessary.*

   - ***User-Specific Alias***

   This configuration applies only to the current user.

   ```sh
   git config --global alias.acm '!C:/Users/%USERNAME%/AppData/Local/Programs/Python/Python313/python.exe C:/Tools/auto-commit-message/main.py' --replace-all
   ```

   *Note: This uses the user-specific Python installation path. The `%USERNAME%` environment variable will be expanded to the current user's name. Adjust the Python path according to your installation if necessary*

   <details>
     <summary>Troubleshooting</summary>

     If you encounter issues creating the Git alias, the `--replace-all` option ensures that any existing alias with the same name is overwritten. If problems persist, consult the following external resources for further assistance:

     - [How to Set Up Git Aliases](https://dev.to/jsdevspace/how-to-set-up-git-aliases-1hge)

     - [Git Basics - Git Aliases](https://git-scm.com/book/ms/v2/Git-Basics-Git-Aliases)
   </details>

## Usage

### Standard Workflow

1. **Stage Your Changes**

   ```sh
   git add .
   ```

   Or selectively stage changes for more precise commit messages:

   ```sh
   git add <path/to/modified/files>
   ```

2. **Generate and Execute Commit**

   ```sh
   git acm
   ```

   The tool will:
   - Analyze staged changes
   - Generate a structured commit message
   - Execute the commit operation

### Advanced Options

- **Review Before Commit**: The system will display the generated commit message and prompt for confirmation
- **Custom Commit Types**: The tool recognizes all standard conventional commit types (see [Commit Types](#commit-types))

## Commit Types

Auto Commit Message follows the [Conventional Commits specification](https://www.conventionalcommits.org/), supporting the following commit types:

| Type | Description |
|------|-------------|
| `build` | Changes affecting build system or external dependencies |
| `ci` | Changes to CI configuration files and scripts |
| `chore` | Routine maintenance tasks and minor changes |
| `docs` | Documentation-only changes |
| `feat` | Introduction of new features |
| `fix` | Bug fixes |
| `perf` | Performance improvements |
| `refactor` | Code changes that neither fix bugs nor add features |
| `revert` | Reverts a previous commit |
| `style` | Changes not affecting code functionality (formatting, etc.) |
| `test` | Adding or correcting tests |
| `security` | Security-related improvements or fixes |

## Configuration

### Global Configuration

The system uses a centralized configuration file at `C:\Tools\auto-commit-message\.env.local` containing the following parameters:

- `GEMINI_API_KEY`: Your Google Gemini API authentication key

### Model Parameters

Advanced users can modify the following parameters in `main.py`:

- `temperature`: Controls creativity level (0.0-1.0)
- `top_p`: Nucleus sampling parameter for response diversity
- `top_k`: Limits vocabulary choices for each token prediction
- `max_output_tokens`: Maximum response length

## Architecture

### Project Structure

```sh
auto-commit-message
├─ .github                      # GitHub config
│  ├─ ISSUE_TEMPLATE            # Issue templates
│  │  ├─ bug_report.md          # Bug report
│  │  ├─ custom.md              # Custom issues
│  │  └─ feature_request.md     # Feature request
│  └─ FUNDING.yml               # Funding info
├─ __init__.py                  # Package init
├─ .gitignore                   # Git ignore
├─ ai_manager.py                # AI manager
├─ CODE_OF_CONDUCT.md           # Code of conduct
├─ config.py                    # Config settings
├─ env_manager.py               # Env manager
├─ exceptions.py                # Exceptions
├─ git_manager.py               # Git manager
├─ LICENSE                      # License info
├─ logging_setup.py             # Logging setup
├─ main.py                      # Main logic
├─ models.py                    # Models
├─ README.md                    # Docs
├─ requirements.txt             # Dependencies
├─ SECURITY.md                  # Security policy
└─ setup.bat                    # Windows setup
```

### Execution Flow

1. **Environment Validation**:
   - Checks for valid Git installation
   - Verifies current directory is a Git repository
   - Validates API key configuration

2. **Change Analysis**:
   - Retrieves staged changes via `git diff --cached`
   - Preprocesses diff content for AI analysis

3. **Message Generation**:
   - Submits preprocessed changes to Google Gemini API
   - Applies structured prompt with formatting requirements
   - Receives AI-generated commit message

4. **Commit Execution**:
   - Displays generated message for review
   - Executes commit operation with validated message

## Contributing

We welcome contributions to improve Auto Commit Message! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-improvement`)
3. Commit your changes using conventional commits (`feat: add amazing improvement`)
4. Push to your branch (`git push origin feature/amazing-improvement`)
5. Open a Pull Request

For more details, please review our [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md).

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

<p align="center">
  <em>Elevate your Git workflow with AI-powered commit messages</em>
</p>

<p align="center">
  Made with precision and care by <a href="https://github.com/idugeni">idugeni</a>
</p>