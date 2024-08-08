import json
import requests
from requests.auth import HTTPBasicAuth
from tokens import JIRA_URL, API_TOKEN, EMAIL


jira_tools = \
[
  {
    "type": "function",
    "function": {
      "name": "get_all_issues",
      "description": "Retrieve all issues from the Jira project 'KAN'",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_all_projects",
      "description": "Retrieve all projects from the Jira instance",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  }
]


def get_issues_by_assignee(assignee_EMAIL):
    # Jira REST API URL for searching issues
    search_url = f"{JIRA_URL}/rest/api/3/search"
    
    # Jira REST API query parameters
    query = {
        'jql': f'assignee = "{assignee_EMAIL}"',
        'maxResults': 1000  # Adjust as needed
    }
    
    # Headers and authentication for the request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    # Make the request to the Jira API
    response = requests.get(search_url, headers=headers, params=query, auth=auth)
    
    # Check for successful response
    if response.status_code == 200:
        issues = response.json()
        return issues['issues']
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None


def assign_issue(issue_key, assignee_EMAIL):
    # Jira REST API URL for assigning an issue
    assign_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/assignee"
    
    # Payload for the request
    payload = {
        'accountId': get_account_id(JIRA_URL, API_TOKEN, EMAIL, assignee_EMAIL)
    }
    
    # Headers and authentication for the request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    # Make the request to the Jira API
    response = requests.put(assign_url, headers=headers, auth=auth, data=json.dumps(payload))
    
    # Check for successful response
    if response.status_code == 204:
        print(f"Issue {issue_key} successfully assigned to {assignee_EMAIL}.")
    else:
        print(f"Failed to assign issue: {response.status_code} - {response.text}")


def get_all_issues():
    # Jira REST API URL for searching issues
    search_url = f"{JIRA_URL}/rest/api/3/search"
    
    # Jira REST API query parameters
    query = {
        'jql': 'project = KAN',
        'maxResults': 1000  # Adjust as needed
    }
    
    # Headers and authentication for the request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    # Make the request to the Jira API
    response = requests.get(search_url, headers=headers, params=query, auth=auth)
    
    # Check for successful response
    if response.status_code == 200:
        issues = response.json()
        print(issues['issues'])
        return json.dumps(issues['issues'])
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None

'''
def get_all_issues():
    # Jira REST API URL for searching issues
    search_url = f"{JIRA_URL}/rest/api/3/search"

    # Jira REST API query parameters
    query = {
        'jql': 'project = KAN',
        'maxResults': 1000  # Adjust as needed
    }

    # Headers and authentication for the request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)

    # Make the request to the Jira API
    response = requests.get(search_url, headers=headers, params=query, auth=auth)

    # Check for successful response
    if response.status_code == 200:
        issues = response.json()['issues']

        # Initialize a list to store the string representations of issues
        issue_strings = []

        # Iterate through each issue and format the values into a string
        for issue in issues:
            issue_str = f"Issue Key: {issue.get('key', 'N/A')}\n"
            fields = issue.get('fields', {})
            issue_str += f"Summary: {fields.get('summary', 'N/A')}\n"
            issue_str += f"Status: {fields.get('status', {}).get('name', 'N/A')}\n"
            issue_str += f"Assignee: {fields.get('assignee', {}).get('displayName', 'Unassigned')}\n"
            issue_str += f"Reporter: {fields.get('reporter', {}).get('displayName', 'N/A')}\n"
            issue_str += f"Created: {fields.get('created', 'N/A')}\n"
            issue_str += f"Updated: {fields.get('updated', 'N/A')}\n"
            issue_str += "-" * 40 + "\n"

            # Append the formatted string to the list
            issue_strings.append(issue_str)
        print('====')
        print(issue_str)
        print('----------')
        # Join all issue strings into a single formatted string
        return "\n".join(issue_strings)
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None
'''
def get_all_projects():
    # Jira REST API URL for getting all projects
    projects_url = f"{JIRA_URL}/rest/api/3/project"
    
    # Headers and authentication for the request
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    # Make the request to the Jira API
    response = requests.get(projects_url, headers=headers, auth=auth)
    
    # Check for successful response
    if response.status_code == 200:
        projects = response.json()
        return projects
    else:
        print(f"Failed to fetch projects: {response.status_code} - {response.text}")
        return None



