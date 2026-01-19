"""Worklog repository implementation."""

from typing import List, Dict, Any
from datetime import datetime

from app.domain.interfaces import IWorklogRepository, IJiraClient
from app.utils.helpers import extract_comment, format_seconds


class WorklogRepository(IWorklogRepository):
    """Repository for worklog data access."""

    def __init__(self, jira_client: IJiraClient):
        self._jira_client = jira_client

    def get_worklogs_by_date_range(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        try:
            jql = f'worklogAuthor = "{account_id}"'
            
            search_result = self._jira_client.search_issues(
                jql=jql,
                fields=["summary", "reporter"],
                max_results=100
            )
        except Exception as e:
            from fastapi import HTTPException
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search Jira issues: {str(e)}"
            )

        issues = search_result.get("issues", [])
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

            worklogs = self._jira_client.get_issue_worklogs(issue_key)

            for wl in worklogs:
                if wl["author"]["accountId"] != account_id:
                    continue

                worklog_date = wl["started"][:10]
                if not (start_date <= worklog_date <= end_date):
                    continue

                formatted_date = datetime.strptime(worklog_date, "%Y-%m-%d").strftime("%d-%m-%Y")

                daily_data.setdefault(worklog_date, {
                    "workDate": worklog_date,
                    "workDateFormatted": formatted_date,
                    "daySummary": {"totalTimeSpentSeconds": 0},
                    "issues": {}
                })

                day_entry = daily_data[worklog_date]
                day_entry["issues"].setdefault(issue_key, {
                    "issueKey": issue_key,
                    "issueSummary": issue_summary,
                    "reportedBy": reporter_info,
                    "worklogSummary": {"totalTimeSpentSeconds": 0},
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

        return self._format_response(daily_data)

    def _format_response(self, daily_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
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
            result.append(day_entry)

        return result
