# 🚀 Auto Commit Message

![Auto Commit Message Logo](https://opengraph.githubassets.com/856c5388bec324b86d5fb9acf0cc386418284ea1/idugeni/auto-commit-message)

Auto Commit Message is an automated script that helps generate structured Git commit messages using AI (Google Gemini) based on repository changes.

[![🔥 Git Commit Like a Pro! Use Gemini AI to Automate Perfect Messages! 🚀](https://img.youtube.com/vi/lbaSAhxPpWY/maxresdefault.jpg)](https://www.youtube.com/watch?v=lbaSAhxPpWY)

## 📂 Project Structure

```sh
📦 auto-commit-message
├── main.py             # Main script to generate commit messages
├── requirements.txt    # Required Python dependencies
├── .gitignore          # Ignore unnecessary files
├── .env.local          # Store API key (automatically created if missing)
├── README-ID.md        # Project documentation (Indonesian)
├── README.md           # Project documentation
├── LICENSE             # Project license
├── CODE_OF_CONDUCT.md  # Contribution code of conduct
└── SECURITY.md         # Security guidelines and issue reporting
```

## 📜 Key Features

✅ **Detects Git Changes**: Captures staged changes in the repository.  
✅ **AI-Powered Commit Messages**: Uses Google Gemini AI to generate clear and standardized commit messages.  
✅ **Repository Validation**: Ensures the working directory is a valid Git repository.  
✅ **Global .env Configuration**: Uses `.env.local` from the global path `C:\Tools\auto-commit-message`.  
✅ **Git Command Shortcut**: Can be executed using `git acm`.  

## 📦 Installation

1️⃣ **Ensure Python is Installed**

   ```sh
   python --version
   ```

   If not installed, download it from [python.org](https://www.python.org/).

2️⃣ **Clone the Repository**

   ```sh
   git clone https://github.com/idugeni/auto-commit-message.git
   ```

   ```sh
   cd auto-commit-message
   ```

3️⃣ **Run the Setup Script**

   ```sh
   run.bat
   ```

   This will copy the project files to `C:\Tools\auto-commit-message/` for global access.

4️⃣ **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

5️⃣ **Set Google Gemini API Key**

- Create a `.env.local` file in `C:\Tools\auto-commit-message` (if not already present).
- Add the following line:

     ```sh
     GEMINI_API_KEY=your_api_key_here
     ```

- Replace `your_api_key_here` with your actual Google Gemini API key.

6️⃣ **Create a Git Alias** (to use `git acm` easily)

   ```sh
   git config --global alias.acm '!C:/Users/%USERNAME%/AppData/Local/Programs/Python/Python313/python.exe C:/Tools/auto-commit-message/main.py'
   ```

## 🚀 Usage

1️⃣ **Ensure your changes are staged**

   ```sh
   git add .
   ```

   or

   ```sh
   git add <modified_file>
   ```

   for maximum results regarding changes to each file

2️⃣ **Run the command for automatic commit**

   ```sh
   git acm
   ```

   The script will automatically generate a commit message and commit the changes 🎉

## 📌 Supported Commit Message Types

This script generates commit messages following the **Conventional Commits** standard:

- `build`: Changes affecting the build system or external dependencies.
- `ci`: Changes related to CI/CD configuration.
- `chore`: Minor changes not affecting source code or tests.
- `docs`: Documentation-only changes.
- `feat`: New feature additions.
- `fix`: Bug fixes.
- `perf`: Performance improvements.
- `refactor`: Code refactoring without changing functionality.
- `revert`: Reverting previous changes.
- `style`: Formatting or whitespace changes (no functional impact).
- `test`: Adding or improving tests.
- `security`: Security-related fixes or enhancements.

## 📜 License

This project is licensed under the **MIT License**. Feel free to use and modify it as needed! 🚀💖

---

Made with ❤️ to simplify your Git workflow! ✨ If you have any suggestions or feature requests, feel free to reach out! 😊
