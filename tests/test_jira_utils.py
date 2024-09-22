import unittest
from unittest import mock
from jira import JIRA
from dimple_utils.jira_utils import (
    setup_jira, get_jira_http_request_headers, fetch_issues, add_comment, rank_issue, create_issue, issue
)

class TestJiraUtils(unittest.TestCase):

    @classmethod
    @mock.patch('dimple_utils.jira_utils.config_utils.get_property')
    @mock.patch('dimple_utils.jira_utils.JIRA')
    def setUpClass(cls, mock_jira_class, mock_get_property):
        """
        Setup JIRA connection before all tests. This is run only once for all test cases.
        """
        # Mock property values for JIRA
        mock_get_property.side_effect = ['https://jira.example.com', 'jira_user', '/path/to/token/file']

        # Mock the file open for reading the token
        with mock.patch('builtins.open', mock.mock_open(read_data='jira_token')):
            setup_jira()

        # Check if JIRA class was instantiated with the correct credentials
        mock_jira_class.assert_called_with(server='https://jira.example.com', basic_auth=('jira_user', 'jira_token'))

    @mock.patch('dimple_utils.jira_utils.get_jira_http_request_headers', return_value={'Authorization': 'Basic encoded_credentials'})
    @mock.patch('dimple_utils.jira_utils.requests.request')  # Patch requests.request instead of requests.put
    def test_rank_issue(self, mock_request, mock_headers):
        """
        Test ranking an issue after another issue.
        """
        # Simulate a successful response from the PUT request
        mock_request.return_value.status_code = 204

        result = rank_issue('TEST-1', 'TEST-2')

        # Ensure the request was made with the correct URL, data, and headers
        mock_request.assert_called_once_with(
            "PUT",
            'https://jira.example.com/rest/agile/1.0/issue/rank',
            data=mock.ANY,
            headers={'Authorization': 'Basic encoded_credentials'}
        )

        # Ensure the result is True on success
        self.assertTrue(result)


    @mock.patch('dimple_utils.jira_utils.jira')  # Mock the global jira object
    @mock.patch('dimple_utils.jira_utils.config_utils.get_property', return_value='project_key')
    def test_fetch_issues(self, mock_get_property, mock_jira):
        """
        Test fetching issues from JIRA.
        """
        # Mock the return value for jira.search_issues
        mock_jira.search_issues.return_value = ['issue_1', 'issue_2']

        # Call the fetch_issues function
        issues = fetch_issues('TEST_PROJECT')

        # Ensure the search_issues method was called with the correct JQL query
        mock_jira.search_issues.assert_called_once_with('project=TEST_PROJECT ORDER BY RANK ASC', maxResults=False)

        # Ensure the result is the list of issues
        self.assertEqual(issues, ['issue_1', 'issue_2'])


    @mock.patch('dimple_utils.jira_utils.jira')  # Mock the global jira object
    def test_add_comment(self, mock_jira):
        """
        Test adding a comment to an issue.
        """
        # Call the function to add a comment
        add_comment('TEST-1', 'This is a test comment.')

        # Ensure add_comment was called on the mock jira object
        mock_jira.add_comment.assert_called_once_with('TEST-1', 'This is a test comment.')


    @mock.patch('dimple_utils.jira_utils.jira')  # Mock the global jira object
    def test_issue(self, mock_jira):
        """
        Test fetching a JIRA issue by key.
        """
        # Mock the return value for jira.issue
        mock_jira.issue.return_value = 'TEST-1 issue data'

        # Call the issue function
        result = issue('TEST-1')

        # Ensure the issue method was called on the mock jira object
        mock_jira.issue.assert_called_once_with('TEST-1')

        # Ensure the result is the expected issue data
        self.assertEqual(result, 'TEST-1 issue data')


    @mock.patch('dimple_utils.jira_utils.jira')  # Mock the global jira object
    def test_create_issue(self, mock_jira):
        """
        Test creating an issue in JIRA.
        """
        fields = {
            'project': {'key': 'TEST_PROJECT'},
            'summary': 'Test issue',
            'description': 'This is a test issue'
        }

        # Call the create_issue function
        create_issue(fields)

        # Ensure jira.create_issue was called with the correct fields
        mock_jira.create_issue.assert_called_once_with(fields=fields)


if __name__ == '__main__':
    unittest.main()
