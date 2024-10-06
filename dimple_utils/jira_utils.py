import base64
import logging
import re
from datetime import datetime

from jira import JIRA
import requests
import json

# Import the config_utils from the dimple_utils package
from dimple_utils import config_utils

logger = logging.getLogger(__name__)

jira = None
board_url = None

# Constants
sprint_custom_field = 'customfield_10020'
jira_http_request_headers = None
JIRA_URL = None
done_status_list = ('Done', 'Resolved', 'Closed', 'Verified', 'Invalid')
done_status_list_str = "('Done', 'Resolved', 'Closed', 'Verified', 'Invalid')"
JIRA_PM_LABELS = ("pm-high", "pm-medium", "pm-low", "pm-neutral")
email_to_user_id_map = {}

def setup_jira():
    """
    Sets up the JIRA connection and configuration using values from config_utils.
    """
    global jira, jira_http_request_headers, JIRA_URL

    # JIRA Configuration from config_utils

    JIRA_URL = config_utils.get_property('jira_url')
    JIRA_USER = config_utils.get_property('jira_user')
    JIRA_TOKEN = config_utils.get_secret("jira_token")

    JIRA_URL = JIRA_URL.strip() if JIRA_URL else None
    JIRA_USER = JIRA_USER.strip() if JIRA_USER else None
    JIRA_TOKEN = JIRA_TOKEN.strip() if JIRA_TOKEN else None

    if not JIRA_URL:
        raise Exception("jira_url property is not configured")

    if not JIRA_USER:
        raise Exception("jira_user property is not configured")

    if not JIRA_TOKEN:
        raise Exception("jira_token property is not configured")


    base64_credentials = base64.b64encode(f"{JIRA_USER}:{JIRA_TOKEN}".encode()).decode()
    jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USER, JIRA_TOKEN), validate=True)


    # Setup HTTP request headers
    jira_http_request_headers = {
        'Authorization': f"Basic {base64_credentials}",
        'Content-Type': 'application/json',
        "Accept": "application/json"
    }

    logger.info(f"JIRA connection setup completed. JIRA_URL={JIRA_URL}, JIRA_USER={JIRA_USER}")


def get_jira_http_request_headers():
    """
    Returns the HTTP request headers for JIRA.
    """
    global jira_http_request_headers
    return jira_http_request_headers


def parse_sprint_field(issue, sprint):

    # Assuming the sprint field is a string that needs to be parsed
    try:
        # Example: remove leading and trailing brackets and split by commas
        sprint_name = sprint.name
        sprint_state = sprint.state
        #print(f"issue={issue.key} sprint_name={sprint_name}, sprint_state={sprint_state}")
        return (sprint_name, sprint_state)
    except Exception as ex:
        print(ex)
        return None

def get_sprint(issue):

    try:
        if hasattr(issue.fields, sprint_custom_field):
            sprint_field = getattr(issue.fields, sprint_custom_field)
            if isinstance(sprint_field, list):
                return sprint_field[0]
            else:
                return sprint_field
        else:
            return None
    except AttributeError as ex:
        print(f"Error getting sprint field for issue {issue.key} ex={ex}")
        return None


def get_relevant_sprint(issue):
    try:
        if hasattr(issue.fields, sprint_custom_field):
            sprint_field = getattr(issue.fields, sprint_custom_field)
            #print(f"GOT SPRINT FIELD {sprint_field}")
        else:
            #print(f"NO SPRINT FIELD")
            return None
    except AttributeError as ex:
        print(f"Error getting sprint field for issue {issue.key} ex={ex}")
        return None

    if not sprint_field:
        return None

    if not isinstance(sprint_field, list):
        sprint_field = [sprint_field]


    #print(sprint_field)
    active_sprint = None
    future_sprint = None

    # Iterate through the Sprints and categorize them
    for sprint in sprint_field:
        # print(f"sprint={sprint}")
        (sprint_name, sprint_state) = parse_sprint_field(issue, sprint)
        if sprint_state == 'active':
            active_sprint = sprint_name
        elif sprint_state == 'future':
            future_sprint = sprint_name

    # Prioritize active Sprint, fallback to future Sprint
    return active_sprint if active_sprint else future_sprint

def fetch_issues(jira_project, num_issues=None, jql_query=None):
    global jira
    logger.info(f"Fetching issues for project {jira_project} with jql_query={jql_query} ...")
    max_results = num_issues if num_issues else False

    # Establishing connection with JIRA
    user_jql = ""
    if jql_query:
        jql_query = jql_query.replace("‘", "'")
        jql_query = jql_query.replace("’", "'")
        user_jql = f"and {jql_query}"

    consolidated_jql_query = f"project={jira_project} {user_jql}".strip() + " ORDER BY RANK ASC"

    logger.info(f"consolidated_jql_query={consolidated_jql_query}")
    issues = jira.search_issues(consolidated_jql_query, maxResults=max_results)

    return issues


def rank_issue(issue, after_issue):
    logger.info(f"Attempting to rank issue {issue} after {after_issue}")
    url = f"{JIRA_URL}/rest/agile/1.0/issue/rank"
    payload = json.dumps({
        "rankAfterIssue": after_issue,
        "issues": [issue]
    })

    response = requests.request(
        "PUT",
        url,
        data=payload,
        headers=get_jira_http_request_headers()
    )
    logger.info(f"ur={url}, response={response}")
    if response.status_code == 204:
        logger.info(f"Successfully ranked issue {issue} before {after_issue}.")
        return True
    else:
        raise Exception(f"Failed to rank issue. Status code: {response.status_code}, Response: {response.text}")
        # logger.error(f"Failed to rank issue. Status code: {response.status_code}, Response: {response.text}")
        # return False

def reorder_issues_from_multiline(input_text):
    lines = input_text.split('\n')
    previous_issue_key = None

    #print(f"lines={lines}")
    logger.info(f"lines={lines}")
    reordered_count = 0
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if not line:  # Skip empty lines
            continue
        if not previous_issue_key:
            previous_issue_key = line.split(',')[0].strip()
            #print(f"Setting previous_issue_key={previous_issue_key}")
            continue
        print(f"line={line}")
        current_issue_key = line.split(',')[0].strip()

        if previous_issue_key:
            try:
                rank_issue(current_issue_key, previous_issue_key)
                reordered_count += 1
                print(f"Successfully ranked {current_issue_key} after {previous_issue_key} reordered_count={reordered_count}")
            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the timestamp
                status_message = (f"An error occurred while ranking {current_issue_key} after {previous_issue_key}: "
                                  f"{e}. Attempted at {current_time}.")
                return "error", status_message
            previous_issue_key = current_issue_key

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the timestamp

    if not reordered_count:
        return "warning", f"No issues reordered. Please provide the list of JIRAs to be reordered. Attempted at {current_time}"

    return "success", f"Successfully reordered {reordered_count} issues. Attempted at {current_time}"


def apply_pm_labels(pm_label, input_text):
    lines = input_text.split('\n')
    previous_issue_key = None

    #print(f"lines={lines}")
    logger.info(f"lines={lines}")
    applied_count = 0
    ignored_count = 0
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if not line:  # Skip empty lines
            continue
        current_issue_key = line.split(',')[0].strip()
        jira_issue = issue(current_issue_key)
        current_labels = jira_issue.fields.labels
        pm_labels = [label for label in current_labels if label in JIRA_PM_LABELS]
        if pm_label not in current_labels or (pm_labels and len(pm_labels) > 1):
            # Check if any of the PM labels are already there
            pm_labels = [label for label in current_labels if label in JIRA_PM_LABELS]
            if pm_labels:
                for current_label in pm_labels:
                    logger.info(f"Removing label {current_label} from issue {current_issue_key}...")
                    current_labels.remove(current_label)
                # current_labels.remove(pm_labels[0])
            current_labels.append(pm_label)
            logger.info(f"Applying label {pm_label} to issue {current_issue_key}...")
            try:
                jira_issue.update(fields={"labels": current_labels})
            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status_message = (f"An error occurred while applying label {pm_label} to issue {current_issue_key}: "
                                  f"{e}. Attempted at {current_time}. Successfully applied {applied_count} labels."
                                  f"Ignored {ignored_count} labels.")
                return "error", status_message
            applied_count += 1
        else:
            logger.info(f"Issue {current_issue_key} already has the label {pm_label}. Ignoring...")
            ignored_count += 1


    stat_message = f"Successfully applied {applied_count} labels. Ignored {ignored_count} labels."
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the timestamp

    if not applied_count:
        return "warning", f"No issues labeled. {stat_message}. Attempted at {current_time}"

    return "success", f"{stat_message}. Attempted at {current_time}"

def create_issue(fields):
    global jira
    logging.info(f"Creating issue with fields={fields}")
    return jira.create_issue(fields=fields)


def update_issue( jira_issue, fields ):
    logging.info(f"Updating issue {jira_issue.key} with fields={fields}")
    jira_issue.update(fields)

def close_issue( jira_issue, comment=None ):
    logging.info(f"Closing issue {jira_issue.key} with comment={comment}")

    if comment:
        add_comment(jira_issue.key, comment)

    transistion_close_id = None
    transitions = jira.transitions(jira_issue.key)
    for transition in transitions:
        if transition['name'].lower() == 'done':
            transistion_close_id = transition['id']
            logging.info(f"Transition ID for Done status found for issue {jira_issue.key}.")
            break

    if not transistion_close_id:
        logger.error(f"Transition ID for Done status not found for issue {jira_issue.key}. Available transitions: "
                     f"{transitions}")
    else:
        jira.transition_issue(jira_issue, transistion_close_id)

def delete_issue( jira_issue ):
    logging.info(f"Deleting issue {jira_issue.key}")
    jira.delete_issue(jira_issue)

def create_issue_link(type, inwardIssue, outwardIssue):
    global jira
    logger.info(f"Creating issue link type={type} inwardIssue={inwardIssue} outwardIssue={outwardIssue}")
    return jira.create_issue_link(type=type, inwardIssue=inwardIssue, outwardIssue=outwardIssue)


def add_comment(key, comment_text):
    global jira
    logger.info(f"Adding comment to issue {key} comment={comment_text}...")
    return jira.add_comment(key, comment_text)


def issue(key):
    global jira
    logger.info(f"Fetching issue {key}...")
    return jira.issue(key)

def get_issues_by_field( jira_project, field_name, field_value):
    global jira
    jql_query = f"{field_name}='{field_value}'"
    logger.info(f"Fetching issues for field_name={field_name} field_value={field_value} jql_query={jql_query} ...")
    return fetch_issues(jira_project, jql_query=jql_query)

def transition_issue(task, fields):
    global jira
    logger.info(f"Transitioning issue {task} with fields={fields}...")
    return jira.transition_issue(task, fields=fields)


def get_story_and_sub_tasks(jira_key):
    story_and_sub_tasks = {"parent": None, "sub_tasks": [] }
    parent = jira.issue(jira_key)
    if parent:
        story_and_sub_tasks["parent"] = parent
        jql_query = f"parent={jira_key}"
        story_and_sub_tasks["sub_tasks"] = fetch_issues(parent.fields.project.key, jql_query=jql_query)
    else:
        logger.error(f"Parent issue {jira_key} not found.")

    return story_and_sub_tasks


def prepare_issue_for_cloning(parent, new_summary, sub_tasks):
    components_for_clone = [{'name': component.name} for component in parent.fields.components]
    sprint = get_sprint(parent)

    description = f"Cloned from original issue: {parent.key}\n\n{parent.fields.description}"

    assignee_id = parent.fields.assignee.accountId if parent.fields.assignee else None

    # Close the parent task
    new_issue_fields = {
        'project': {'key': parent.fields.project.key},
        'summary': new_summary,
        'description': description,
        'components': components_for_clone,
        'issuetype': {'name': parent.fields.issuetype.name},
        'reporter': {'id': parent.fields.reporter.accountId},
        'assignee': {'id': assignee_id}
    }

    if sprint:
        new_issue_fields[sprint_custom_field] = sprint.id

    link_list = []

    for link in parent.fields.issuelinks:
        linked_issue_key = None
        link_type = None

        is_inward = False
        if hasattr(link, "outwardIssue"):
            linked_issue_key = link.outwardIssue.key
            link_type = link.type.outward
        elif hasattr(link, "inwardIssue"):
            linked_issue_key = link.inwardIssue.key
            link_type = link.type.inward
            is_inward = True

        if linked_issue_key:
            # Recreate the link between the clone_issue_key and the linked_issue_key
            link_list.append({"type": link_type, "inwardIssue": linked_issue_key if is_inward else None,
                              "outwardIssue": linked_issue_key if not is_inward else None})

    for link_data in link_list:
        logger.info(f"Link type={link_data.get('type')} inwardIssue={link_data.get('inwardIssue')} outwardIssue={link_data.get('outwardIssue')}")

    sub_tasks_to_move = []
    for sub_task in sub_tasks:
        # For now we are setting the issue attribute. The split unfinished JIRAs uses a lot more
        task_data = {"issue": sub_task}
        sub_tasks_to_move.append(task_data)


    cloned_issue = {"fields": new_issue_fields, "comment_text": f"This issue is a clone of {parent.key}.",
                    "link_list": link_list, "sub_tasks_to_move": sub_tasks_to_move, "parent": parent,
                    "not_done_sub_tasks": None}
    return cloned_issue


def clone_jira(to_be_cloned_issue):
    parent = to_be_cloned_issue["parent"]
    #Create the new issue
    fields = to_be_cloned_issue["fields"]
    new_issue = create_issue(fields=fields)
    logger.info(f"new_issue={new_issue.key}")

    #Add the comment to the cloned issue
    comment_text = to_be_cloned_issue["comment_text"]
    add_comment(new_issue.key, comment_text)

    #Recreate the links between the clone_issue_key and the linked_issue_key
    link_list = to_be_cloned_issue["link_list"]
    for link in link_list:
        inward_issue = link.get("inwardIssue") if link.get("inwardIssue") else new_issue.key
        outward_issue = link.get("outwardIssue") if link.get("outwardIssue") else new_issue.key

        create_issue_link(
            type=link.get("type"),
            inwardIssue=inward_issue,
            outwardIssue=outward_issue
        )

    create_issue_link(type="clones", inwardIssue=new_issue.key, outwardIssue=parent.key)

    for sub_task in to_be_cloned_issue["sub_tasks_to_move"]:
        fields = {'parent': {'key': new_issue.key}}
        # logger.info(f"Moving sub-task {sub_task.get('Key')} from {parent.key} to {new_issue.key}")
        # latest_sub_task = issue(sub_task.get('Key'))
        # latest_sub_task.update(fields=fields)
        sub_task_issue = sub_task.get("issue")
        logger.info(f"Moving sub-task {sub_task_issue.key} from {parent.key} to {new_issue.key}")
        sub_task_issue.update(fields=fields)

    return new_issue


def clone_jiras(to_be_cloned_list):
    new_issue_list = []
    for to_be_cloned_issue in to_be_cloned_list:
        new_issue_list.append(clone_jira(to_be_cloned_issue))
    return new_issue_list

def get_board_id():
    global jira, board_url
    match = re.search(r'boards/(\d+)', board_url)
    if match:
        return match.group(1)
    else:
        logger.error(f"Board ID not found in the JIRA URL {JIRA_URL}")

def get_active_sprint():
    global jira
    board_id = get_board_id()
    if board_id:
        try:
            sprints = jira.sprints(board_id, state="active")
            if sprints:
                return sprints[0]
        except IndexError:
            logger.warning(f"No active sprint found for board_id={board_id}")
    return None

def set_board_url(url):
    global board_url
    board_url = url

def get_user_id(email_id):
    global jira
    user_id = email_to_user_id_map.get(email_id)
    if not user_id:
        user = jira.search_users(query=email_id)
        if user:
            user_id = user[0].accountId
            email_to_user_id_map[email_id] = user_id
        else:
            logger.error(f"User with email {email_id} not found.")
    return user_id

####### Borrowed from https://github.com/eshack94/md-to-jira. Works like a charm! ########
def convert_line(line):
    # Convert headers
    line = re.sub(r'^#{6}\s*(.+)', r'h6. \1', line)
    line = re.sub(r'^#{5}\s*(.+)', r'h5. \1', line)
    line = re.sub(r'^#{4}\s*(.+)', r'h4. \1', line)
    line = re.sub(r'^#{3}\s*(.+)', r'h3. \1', line)
    line = re.sub(r'^#{2}\s*(.+)', r'h2. \1', line)
    line = re.sub(r'^#\s*(.+)', r'h1. \1', line)

    # Convert bold and italic
    line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
    line = re.sub(r'__(.+?)__', r'*\1*', line)
    line = re.sub(r'\*(.+?)\*', r'_\1_', line)
    line = re.sub(r'_(.+?)_', r'_\1_', line)

    # Convert inline code
    line = re.sub(r'`([^`]+)`', r'{{\1}}', line)

    # Convert strikethrough
    line = re.sub(r'~~(.+?)~~', r'-\1-', line)

    # Convert links
    line = re.sub(r'\[(.*?)\]\((.+?)\)', r'[\1|\2]', line)

    # Convert unordered lists
    line = re.sub(r'^\*\s+', r'- ', line)

    # Convert GFM task lists
    line = re.sub(r'^\s*-\s*\[(x|X| )\]', lambda match: f'[{match.group(1)}]', line)

    return line


def convert_multiline_elements(content):
    # Convert multiline fenced code blocks
    content = re.sub(r'```(\w+)?\n(.*?)\n```', process_code_block, content, flags=re.MULTILINE | re.DOTALL)

    # Convert indented code blocks
    content = re.sub(r'((?:^ {4}.*\n?)+)', process_indented_code_block, content, flags=re.MULTILINE)

    return content


def process_code_block(match):
    lang = match.group(1)
    code = match.group(2)
    if lang:
        return f'{{code:{lang}}}\n{code}\n{{code}}'
    else:
        return f'{{code}}\n{code}\n{{code}}'


def process_indented_code_block(match):
    code = match.group(1)
    # Remove the leading 4 spaces or tab from each line
    code = re.sub(r'^ {4}|\t', '', code, flags=re.MULTILINE)
    return f'{{code}}\n{code}{{code}}\n'


def markdown_to_jira(content):
    content = convert_multiline_elements(content)

    # Process the lines
    # add toggle flag to keep track of whether we're in a code block or not
    # so we don't convert # characters in code blocks
    # toggles on when we enter a code block and toggles off when we exit
    # toggle state determines whether we convert the line or not
    in_code_block = False
    jira_lines = []
    for line in content.splitlines():
        if line.startswith("```") or line.startswith("{code"):
            in_code_block = not in_code_block

        if not in_code_block:
            line = convert_line(line)
        jira_lines.append(line)

    # Create a string from the converted lines
    return '\n'.join(jira_lines)
#######  End borrowed code ########
