"""Worklog repository implementation."""

from typing import List, Dict, Any
from datetime import datetime

from app.domain.interfaces import IWorklogRepository, IJiraClient
from app.core.base import BaseRepository
from app.core.exceptions import RepositoryError, ExternalServiceError
from app.utils.helpers import extract_comment, format_seconds


class WorklogRepository(BaseRepository, IWorklogRepository):
    """Repository for worklog data access."""

    def __init__(self, jira_client: IJiraClient):
        super().__init__()
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
                fields=["summary", "reporter", "issuetype", "status", "priority", "assignee", "timeoriginalestimate"],
                max_results=100
            )
        except ExternalServiceError:
            raise
        except Exception as e:
            self._handle_error(
                error=e,
                operation="get_worklogs_by_date_range",
                context={
                    "account_id": account_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        issues = search_result.get("issues", [])
        daily_data = {}

        for issue in issues:
            issue_key = issue["key"]
            fields = issue["fields"]
            issue_summary = fields["summary"]
            reporter = fields.get("reporter", {})
            assignee = fields.get("assignee", {})
            issue_type = fields.get("issuetype", {})
            status = fields.get("status", {})
            priority = fields.get("priority", {})
            original_estimate = fields.get("timeoriginalestimate")

            reporter_info = {
                "accountId": reporter.get("accountId") if reporter else None,
                "displayName": reporter.get("displayName") if reporter else "Unknown"
            }

            assignee_info = {
                "accountId": assignee.get("accountId") if assignee else None,
                "displayName": assignee.get("displayName") if assignee else "Unassigned"
            }

            issue_type_info = {
                "name": issue_type.get("name") if issue_type else "Unknown",
                "iconUrl": issue_type.get("iconUrl") if issue_type else None
            }

            status_info = {
                "name": status.get("name") if status else "Unknown",
                "statusCategory": status.get("statusCategory", {}).get("name") if status else None
            }

            priority_info = {
                "name": priority.get("name") if priority else "Unknown",
                "iconUrl": priority.get("iconUrl") if priority else None
            }

            try:
                worklogs = self._jira_client.get_issue_worklogs(issue_key)
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch worklogs for issue {issue_key}",
                    extra={"issue_key": issue_key},
                    exc_info=e
                )
                continue

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
                    "assignee": assignee_info,
                    "issueType": issue_type_info,
                    "status": status_info,
                    "priority": priority_info,
                    "originalEstimate": original_estimate,
                    "originalEstimateFormatted": format_seconds(original_estimate) if original_estimate else None,
                    "worklogSummary": {"totalTimeSpentSeconds": 0},
                    "worklogs": []
                })

                issue_entry = day_entry["issues"][issue_key]
                time_seconds = wl["timeSpentSeconds"]

                # Extract worklog author info
                worklog_author = wl.get("author", {})
                worklog_author_info = {
                    "accountId": worklog_author.get("accountId"),
                    "displayName": worklog_author.get("displayName", "Unknown")
                }

                # Parse started timestamp
                started_raw = wl.get("started", "")
                started_date = started_raw[:10] if started_raw else ""
                started_time = ""
                if len(started_raw) >= 19:
                    try:
                        started_dt = datetime.fromisoformat(started_raw.replace("Z", "+00:00").split("+")[0])
                        started_time = started_dt.strftime("%H:%M")
                    except:
                        started_time = started_raw[11:16] if len(started_raw) > 16 else ""

                # Parse updated timestamp
                updated_raw = wl.get("updated", "")
                updated_formatted = ""
                if updated_raw:
                    try:
                        updated_dt = datetime.fromisoformat(updated_raw.replace("Z", "+00:00").split("+")[0])
                        updated_formatted = updated_dt.strftime("%d-%m-%Y %H:%M")
                    except:
                        updated_formatted = updated_raw[:16] if len(updated_raw) > 16 else updated_raw

                issue_entry["worklogs"].append({
                    "worklogId": wl["id"],
                    "comment": extract_comment(wl.get("comment")),
                    "timeSpentSeconds": time_seconds,
                    "timeSpentFormatted": format_seconds(time_seconds),
                    "started": started_raw,
                    "startedDate": started_date,
                    "startedTime": started_time,
                    "updated": updated_raw,
                    "updatedFormatted": updated_formatted,
                    "author": worklog_author_info
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
