# Dimple Utils

Dimple Utils is a collection of Python utility wrappers for common libraries, designed to simplify and standardize configurations, logging, and integrations with external services like Slack, JIRA, GitHub, GitLab, SendGrid, and AWS Lambda.

## Features
- **Config Utilities**: Load and manage configuration properties from default and override files.
- **Logging Utilities**: Centralized logging support (to be integrated).
- **Slack Integration**: Easy-to-use wrappers for interacting with Slack's API.
- **JIRA Integration**: Simple methods to interact with JIRA.
- **GitHub & GitLab**: Access GitHub and GitLab repositories, issues, and more.
- **SendGrid**: Send emails via SendGrid with minimal setup.
- **AWS Lambda**: Wrappers to simplify working with AWS Lambda functions.

## When using as a library in another repo

```
git submodule add -b main https://github.com/dbosco/dimple_utils.git libs/dimple_utils
git submodule update --init --recursive
```

```
git add .gitmodules libs/dimple_utils
git commit -m "Add dimple_utils as submodule (track main)"
git push
```

### Local development

```
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e ./libs/dimple_utils
pip install -e .      # your app
```

### CI/CD

```
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

## Updating Dimple Utils

One-time setup (each dev):

```
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

Updating:

```
# work inside the submodule
cd libs/dimple_utils

# avoid detached HEAD; create a feature branch
git switch -c feat/some-improvement

# edit files...
git add -A
git commit -m "Improve X; fix Y"

# push branch to YOUR fork
git push myfork HEAD

# open PR on GitHub from your fork → upstream (dbosco/dimple_utils)
# after PR merges:
git fetch origin
git switch main
git pull origin main

cd ../..
# bump the parent’s pointer to the new submodule commit
git add libs/dimple_utils
git commit -m "Bump dimple_utils to <short-sha>"
git push
```

This keeps .gitmodules aware of the branch, while still pinning on commit until you commit the pointer.

```
git submodule set-branch --branch main libs/dimple_utils
git add .gitmodules
git commit -m "Track dimple_utils main"
git push
```

To bump to the latest upstream main:

```
git submodule update --remote libs/dimple_utils
git add libs/dimple_utils
git commit -m "Bump dimple_utils to latest main"
git push
```

## Installation

To install the project, simply run:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install the Required Libraries

```bash
pip install -r requirements.txt
```

## Installing editable mode for development

```bash
pip install -e .
```

## Using from another project locally
> Note: This should be where the setup.py file is located.
```shell
pip install -e /path/to/dimple-utils
```
And to uninstall:
```shell
pip uninstall dimple-utils
```

## Running the tests

```bash
python3 -m unittest discover -s tests
```

Create a source distribution:
```shell
python setup.py sdist
```

## Testing modules

```shell
python3 -m unittest tests.test_logging_utils
```