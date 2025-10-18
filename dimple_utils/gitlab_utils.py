import logging

from dimple_utils import config_utils
#pip install python-gitlab
import gitlab

gl = None

def setup_gitlab():
    global gl
    """
    Setup the GitLab client with the required credentials.
    """
    # Load the GitLab credentials from the configuration
    gitlab_url = config_utils.get_property("gitlab_url")
    gitlab_token = config_utils.get_secret("gitlab_token")

    logging.info(f"Setting up GitLab client for URL: {gitlab_url}")
    # Initialize the GitLab client
    gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token)

def get_all_projects():
    """
    Get all projects from GitLab.
    """
    return gl.projects.list()

def get_project(project_id):
    """
    Get a GitLab project by its ID or path with namespace (e.g., 'group/project').
    """
    return gl.projects.get(project_id)

def get_issues(project_id):
    """
    Get all issues for a given project.
    """
    project = get_project(project_id)
    return project.issues.list()

def get_merge_requests(project_id):
    """
    Get all merge requests for a given project.
    """
    project = get_project(project_id)
    return project.mergerequests.list()
