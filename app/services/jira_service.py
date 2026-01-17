import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

from app.core.config import (
    JIRA_EMAIL,
    JIRA_API_TOKEN,
    JIRA_DOMAIN
)
from app.utils.helpers import extract_comment, format_seconds

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

HEADERS = {
    "Accept": "application/json"
}


def get_worklog_summary(account_id: str, start_date: str, end_date: str):
    """Fetch and summarize Jira work logs for a user within a date range."""
    jql = (
        f'worklogAuthor = "{account_id}" '
        f'AND worklogDate >= {start_date} '
        f'AND worklogDate <= {end_date}'
    )

    search_url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"

    params = {
        "jql": jql,
        "fields": "summary,reporter",
        "startAt": 0,
        "maxResults": 100
    }

    response = requests.get(search_url, headers=HEADERS, auth=auth, params=params)
    response.raise_for_status()

    issues = response.json().get("issues", [])
    daily_data = {}

    for issue in issues:
        issue_key = issue["key"]
        fields = issue["fields"]

        issue_summary = fields["summary"]
        reporter = fields.get("reporter", {})

        reporter_info = {
            "accountId": reporter.get("accountId"),
            "displayName": reporter.get("displayName")
        }

        worklog_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/worklog"
        wl_response = requests.get(worklog_url, headers=HEADERS, auth=auth)
        wl_response.raise_for_status()

        for wl in wl_response.json().get("worklogs", []):
            if wl["author"]["accountId"] != account_id:
                continue

            worklog_date = wl["started"][:10]
            if not (start_date <= worklog_date <= end_date):
                continue

            formatted_date = datetime.strptime(worklog_date, "%Y-%m-%d").strftime("%d-%m-%Y")

            daily_data.setdefault(worklog_date, {
                "workDate": worklog_date,
                "workDateFormatted": formatted_date,
                "daySummary": {
                    "totalTimeSpentSeconds": 0
                },
                "issues": {}
            })

            day_entry = daily_data[worklog_date]

            day_entry["issues"].setdefault(issue_key, {
                "issueKey": issue_key,
                "issueSummary": issue_summary,
                "reportedBy": reporter_info,
                "worklogSummary": {
                    "totalTimeSpentSeconds": 0
                },
                "worklogs": []
            })

            issue_entry = day_entry["issues"][issue_key]
            time_seconds = wl["timeSpentSeconds"]

            issue_entry["worklogs"].append({
                "worklogId": wl["id"],
                "comment": extract_comment(wl.get("comment")),
                "timeSpentSeconds": time_seconds,
                "timeSpentFormatted": format_seconds(time_seconds)
            })

            issue_entry["worklogSummary"]["totalTimeSpentSeconds"] += time_seconds
            day_entry["daySummary"]["totalTimeSpentSeconds"] += time_seconds

    final_response = []

    for day in sorted(daily_data):
        day_entry = daily_data[day]

        issues_list = []
        for issue in day_entry["issues"].values():
            total_seconds = issue["worklogSummary"]["totalTimeSpentSeconds"]
            issue["worklogSummary"]["totalTimeSpentFormatted"] = format_seconds(total_seconds)
            issues_list.append(issue)

        total_day_seconds = day_entry["daySummary"]["totalTimeSpentSeconds"]
        day_entry["daySummary"]["totalTimeSpentFormatted"] = format_seconds(total_day_seconds)
        day_entry["issues"] = issues_list

        final_response.append(day_entry)

    return final_response
