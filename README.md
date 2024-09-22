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

## Running the tests

```bash
python3 -m unittest discover -s tests
```

Create a source distribution:
```shell
python setup.py sdist
```