
# Updating Dimple Utils - Cursor Instructions

This guide provides step-by-step instructions for updating the Dimple Utils submodule in your project using Cursor IDE.

## 📋 Prerequisites

- Cursor IDE installed
- Git configured with your credentials
- Python 3.11+ installed
- Access to the upstream repository (dbosco/dimple_utils)

## 🚀 Initial Setup (One-time per developer)

### 1. Environment Setup

```bash
# Navigate to your project root
cd /path/to/your/project

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Update pip
pip install -U pip

# Install dimple_utils in editable mode
pip install -e ./libs/dimple_utils

# Install your main project
pip install -e .
```

### 2. Git Submodule Configuration

```bash
# Ensure submodule is properly initialized
git submodule sync --recursive
git submodule update --init --recursive

# Set submodule to track main branch
git submodule set-branch --branch main libs/dimple_utils
git add .gitmodules
git commit -m "Track dimple_utils main branch"
git push
```

## 🔄 Making Updates to Dimple Utils

### Step 1: Navigate to Submodule

```bash
# Always work inside the submodule directory
cd libs/dimple_utils
```

### Step 2: Create Feature Branch

```bash
# Check current status
git status

# Create and switch to feature branch (avoid detached HEAD)
git switch -c feat/your-improvement-name

# Verify you're on the new branch
git branch
```

### Step 3: Make Your Changes

In Cursor IDE:
1. Open the `libs/dimple_utils` directory
2. Edit the necessary files (Python modules, tests, documentation)
3. Follow the project's coding standards
4. Update version in `setup.py` if needed
5. Update `requirements.txt` if adding new dependencies

### Step 4: Test Your Changes

```bash
# Run tests to ensure nothing is broken
python -m unittest discover -s tests

# Or run specific test modules
python -m unittest tests.test_your_module

# Install in editable mode to test integration
pip install -e .
```

### Step 5: Commit Changes

```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "feat: add new utility function for X
- Implemented Y feature
- Fixed Z bug
- Updated documentation"

# Verify commit
git log --oneline -1
```

### Step 6: Push to Your Fork

```bash
# Add your fork as remote (if not already added)
git remote add myfork https://github.com/YOUR_USERNAME/dimple_utils.git

# Push your feature branch
git push myfork feat/your-improvement-name
```

### Step 7: Create Pull Request

1. Go to GitHub: https://github.com/dbosco/dimple_utils
2. Click "New Pull Request"
3. Select your fork and feature branch
4. Fill in PR description with:
   - What changes were made
   - Why the changes were necessary
   - Any breaking changes
   - Testing performed
5. Request review from maintainers
6. Wait for approval and merge

### Step 8: Update Parent Repository

After your PR is merged:

```bash
# Return to parent repository
cd ../..

# Fetch latest changes
git fetch origin

# Switch to main branch
git switch main
git pull origin main

# Update submodule to latest commit
git submodule update --remote libs/dimple_utils

# Stage the submodule update
git add libs/dimple_utils

# Commit the submodule pointer update
git commit -m "Bump dimple_utils to <short-commit-sha>"

# Push changes
git push
```

## 🔄 Updating to Latest Upstream Changes

To pull in changes made by others:

```bash
# Update submodule to latest upstream main
git submodule update --remote libs/dimple_utils

# Stage the update
git add libs/dimple_utils

# Commit the update
git commit -m "Bump dimple_utils to latest main"

# Push changes
git push
```

## 🧪 CI/CD Configuration

For automated testing, use this GitLab CI configuration:

```yaml
image: python:3.11

variables:
  PIP_DISABLE_PIP_VERSION_CHECK: "1"
  PIP_NO_CACHE_DIR: "1"

before_script:
  - python -V
  - git submodule sync --recursive
  - git submodule update --init --recursive
  - python -m venv .venv
  - . .venv/bin/activate
  - pip install -U pip
  - pip install ./libs/dimple_utils
  - pip install -e .

test:
  stage: test
  script:
    - pytest -q
```

## 🚨 Troubleshooting

### Common Issues

1. **Detached HEAD State**
   ```bash
   # Always create a feature branch before making changes
   git switch -c feat/your-branch-name
   ```

2. **Submodule Not Updating**
   ```bash
   # Force update submodule
   git submodule update --remote --force libs/dimple_utils
   ```

3. **Merge Conflicts**
   ```bash
   # Resolve conflicts in submodule
   cd libs/dimple_utils
   git status
   # Edit conflicted files
   git add .
   git commit -m "Resolve merge conflicts"
   ```

4. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ./libs/dimple_utils
   ```

## 📝 Best Practices

- Always work in feature branches
- Write descriptive commit messages
- Test changes before committing
- Update documentation when adding features
- Follow semantic versioning for releases
- Keep submodule up to date with upstream changes
- Use meaningful branch names (feat/, fix/, docs/, etc.)

## 🔗 Useful Commands Reference

```bash
# Check submodule status
git submodule status

# Update all submodules
git submodule update --remote --recursive

# Check submodule branch
git config --file .gitmodules --get submodule.libs/dimple_utils.branch

# Remove submodule (if needed)
git submodule deinit libs/dimple_utils
git rm libs/dimple_utils
git commit -m "Remove dimple_utils submodule"
```
