import unittest
from unittest.mock import patch, MagicMock

from dimple_utils.gitlab_utils import setup_gitlab, get_all_projects, get_project, get_issues, get_merge_requests

class TestGitlabUtils(unittest.TestCase):
    @patch('dimple_utils.config_utils.get_property')
    @patch('dimple_utils.config_utils.get_secret') 
    @patch('gitlab.Gitlab')
    def test_setup_gitlab(self, mock_gitlab, mock_get_secret, mock_get_property):
        # Setup mock returns
        mock_get_property.return_value = "https://gitlab.example.com"
        mock_get_secret.return_value = "mock_token"
        mock_gitlab_instance = MagicMock()
        mock_gitlab.return_value = mock_gitlab_instance

        # Call the function
        setup_gitlab()

        # Verify the calls
        mock_get_property.assert_called_once_with("gitlab_url")
        mock_get_secret.assert_called_once_with("gitlab_token")
        mock_gitlab.assert_called_once_with(
            url="https://gitlab.example.com",
            private_token="mock_token"
        )

    @patch('dimple_utils.gitlab_utils.gl')
    def test_get_all_projects(self, mock_gl):
        # Setup mock
        mock_projects = [MagicMock(), MagicMock()]
        mock_gl.projects.list.return_value = mock_projects

        # Call function
        result = get_all_projects()

        # Verify
        self.assertEqual(result, mock_projects)
        mock_gl.projects.list.assert_called_once()

    @patch('dimple_utils.gitlab_utils.gl')
    def test_get_project(self, mock_gl):
        # Setup mock
        mock_project = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        project_id = "group/project"

        # Call function
        result = get_project(project_id)

        # Verify
        self.assertEqual(result, mock_project)
        mock_gl.projects.get.assert_called_once_with(project_id)

    @patch('dimple_utils.gitlab_utils.get_project')
    def test_get_issues(self, mock_get_project):
        # Setup mock
        mock_project = MagicMock()
        mock_issues = [MagicMock(), MagicMock()]
        mock_project.issues.list.return_value = mock_issues
        mock_get_project.return_value = mock_project
        project_id = 123

        # Call function
        result = get_issues(project_id)

        # Verify
        self.assertEqual(result, mock_issues)
        mock_get_project.assert_called_once_with(project_id)
        mock_project.issues.list.assert_called_once()

    @patch('dimple_utils.gitlab_utils.get_project')
    def test_get_merge_requests(self, mock_get_project):
        # Setup mock
        mock_project = MagicMock()
        mock_mrs = [MagicMock(), MagicMock()]
        mock_project.mergerequests.list.return_value = mock_mrs
        mock_get_project.return_value = mock_project
        project_id = 123

        # Call function
        result = get_merge_requests(project_id)

        # Verify
        self.assertEqual(result, mock_mrs)
        mock_get_project.assert_called_once_with(project_id)
        mock_project.mergerequests.list.assert_called_once()

if __name__ == '__main__':
    unittest.main() 