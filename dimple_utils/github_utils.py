import logging

from dimple_utils import config_utils
#pip install PyGithub
from github import Github

github = None

def setup_github():
    global github

    """
    Setup the GitHub client with the required credentials.
    """
    # Load the GitHub credentials from the configuration
    github_user = config_utils.get_property("github_user")
    github_token = config_utils.get_secret("github_token")

    logging.info(f"Setting up GitHub client for user: {github_user}")
    # Initialize the GitHub client
    github = Github(github_user, github_token)

def get_repo(repo_name):
    return github.get_repo(repo_name)

def get_issues(repo_name):
    repo = get_repo(repo_name)
    return repo.get_issues()
