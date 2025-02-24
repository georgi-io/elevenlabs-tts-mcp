# Development Tools

This directory contains various development and productivity tools used in the project. These tools are designed to help developers and product managers with common tasks and maintain consistency across the codebase.

## Directory Structure

```
.dev-tools/
├── prompts/           # AI prompt templates for various tasks
│   ├── prompt_pr.md   # PR description generation template
│   ├── prompt_commit.md # Commit message generation template
│   └── prompt_user_story.md # User story generation template
│
└── scripts/          # Development utility scripts
    ├── generate_git_diffs.py  # Script for generating git diffs
    ├── check_env_files.py  # Validates environment files across all services
    ├── pyproject.toml       # Poetry project configuration
    ├── .env.example        # Example environment variables
    └── .env               # Your local environment variables (git-ignored)
```

## Tools Overview

### Prompts

The `prompts/` directory contains templates for AI-assisted tasks:

- `prompt_pr.md`: Template for generating detailed pull request descriptions
- `prompt_commit.md`: Template for creating meaningful commit messages
- `prompt_user_story.md`: Template for creating well-structured user stories as GitHub issues

### Scripts

The `scripts/` directory contains utility scripts:

- `generate_git_diffs.py`: Python script for generating git diffs between branches and collecting commit messages
- `check_env_files.py`: Validates environment files across all services
  - Checks for missing .env files against .env.example templates
  - Ensures all required variables are set
  - Detects example/placeholder values that need to be replaced
  - Validates against .gitignore patterns
  - Provides clear progress indicators and summary reports

## Setup

### Environment Variables

1. Create your local environment file:
   ```bash
   cd .dev-tools/scripts
   cp .env.example .env
   ```

2. Adjust the variables in `.env` if needed:
   - `GIT_DIFF_BRANCH`: The branch to compare against (defaults to `origin/dev` for PRs)
   - Note: Most PRs should be created against the `dev` branch. Use `origin/main` only for hotfixes or release PRs.

### Python Dependencies

1. Install Poetry if not already installed:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   cd .dev-tools/scripts
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

### Workflow: Creating User Stories with AI

1. In Cursor's Composer:
   - Reference or drag in `prompt_user_story.md`
   - Describe what you want to achieve in your user story
   - The AI will analyze your input and the codebase to create a comprehensive user story
   - Review and confirm the generated story
   - The AI will help create a GitHub issue with proper project assignment

2. The generated user story will include:
   - Business requirements from a Product Manager's perspective
   - Technical analysis from an Engineering Manager's perspective
   - Implementation approach and considerations
   - Proper GitHub issue metadata and project assignment

### Workflow: Creating Commits with AI

1. Generate the necessary git diffs:
   ```bash
   cd .dev-tools/scripts
   poetry run python generate_git_diffs.py
   ```
   This creates three files in the `temp_output` directory:
   - `TEMP_GIT_commit_diff.txt`: Current changes to be committed
   - `TEMP_GIT_pr_diff.txt`: Changes compared to target branch
   - `TEMP_GIT_pr_commit_messages.txt`: Commit messages history

2. In Cursor's Composer:
   - Reference or drag in `prompt_commit.md`
   - Reference or drag in `TEMP_GIT_commit_diff.txt`
   - Click Submit
   - Cursor will generate a meaningful commit message based on your changes

### Workflow: Creating Pull Requests with AI

1. Ensure correct comparison branch:
   - Check `.env` file in scripts directory
   - By default, it's set to `origin/dev` for normal feature PRs
   - Change to `origin/main` only for hotfixes or release PRs
   - This determines which branch your changes are compared against

2. Generate the git diffs:
   ```bash
   cd .dev-tools/scripts
   poetry run python generate_git_diffs.py
   ```

3. In Cursor's Composer:
   - Reference or drag in `prompt_pr.md`
   - Reference or drag in `TEMP_GIT_pr_diff.txt`
   - Reference or drag in `TEMP_GIT_pr_commit_messages.txt`
   - Click Submit
   - Cursor will generate a detailed PR description based on your changes and commit history

### Tips

- The default target branch is `dev` as most PRs should go there
- Only use `main` as target for hotfixes or release PRs
- The generated files in `temp_output` are temporary and will be overwritten on each run
- You can reference these files in any Cursor Composer chat to generate commit messages or PR descriptions

### Workflow: Checking Environment Files

1. Run the environment checker:
   ```bash
   cd .dev-tools/scripts
   poetry run python check_env_files.py
   ```

2. The script will:
   - Scan the project for service directories
   - Load and respect .gitignore patterns
   - Check each service's environment configuration
   - Provide a detailed report showing:
     - ✅ Properly configured environment files
     - ❌ Missing environment files
     - ⚠️  Variables with example values
     - ⚠️  Extra variables not in example files

3. Fix any issues reported:
   - Create missing .env files based on .env.example templates
   - Fill in required variables
   - Replace example/placeholder values with real ones
   - Review extra variables to ensure they're needed

## Contributing

When adding new tools:
1. Create appropriate subdirectories based on tool type
2. Include clear documentation
3. Update this README with new tool descriptions
4. For Python scripts:
   - Add dependencies to `pyproject.toml` using Poetry
   - Follow the code style defined in `pyproject.toml`
   - Update setup instructions if needed 
