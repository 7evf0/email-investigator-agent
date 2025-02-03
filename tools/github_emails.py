import requests
import random
import json

from smolagents import tool, CodeAgent, OpenAIServerModel, ManagedAgent

@tool
def fetch_github_pr_commits(owner: str, repo: str, count: int) -> object:
    """
    Fetch GitHub repository commits and outputs json including commit message, committer, date and verification to be used in the Github PR notification emails.

    Args:
        owner: Github username of the owner of the specific public repository that is going to be used.
        repo: Github repository name of the specific public repository that is going to be used.
        count: Count of how many commit samples should be fetched from the GitHub repository.
    """

    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits")
    response = json.loads(response.text)

    # Parsing the JSON data
    parsed_commits = []

    for commit in response:

        message = commit["commit"]["message"]

        # Exclude commits with the unwanted message pattern
        if "Automatic changelog for PR" not in message:
            parsed_commits.append({
                "message": message,
                "committer_name": commit["commit"]["committer"]["name"],
                "commit_number": commit["sha"],
                "commit_date": commit["commit"]["committer"]["date"],
                "verified": commit["commit"]["verification"]["verified"]
            })

    random_commits = random.sample(parsed_commits, min(count, len(parsed_commits)))

    return random_commits

@tool
def summarize_commit_message(msg: str) -> str:
    """
        Summarize the large message texts for more concise definition for the email.

        Args:
            msg: GitHub commit message
    """

    if len(msg) > 250:
        return msg[:250] + "..."
    else:
        return msg