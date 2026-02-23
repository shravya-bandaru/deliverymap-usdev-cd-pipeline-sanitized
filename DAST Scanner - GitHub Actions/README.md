# DAST Scanner - GitHub Actions

This folder contains the GitHub Actions equivalents of the Azure DevOps DAST Scanner pipeline files.

## File Mapping

| ADO Pipeline File | GitHub Actions File | Description |
|---|---|---|
| `DAST-Scan.yaml` | `dast-scan.yml` | Main workflow — entry point with schedule, environment selection, and Netsparker config |
| `scan-base.yaml` | `scan-base.yml` | Reusable workflow — generic scan orchestrator handling artifacts, pre/post steps |
| `scan-netsparker.yaml` | `scan-netsparker.yml` | Reusable workflow — Netsparker-specific scan using Invicti REST API |

## Prerequisites

Set the following **GitHub Secrets** in your repository:

| Secret | Description |
|---|---|
| `NETSPARKER_USER_ID` | Invicti API User ID |
| `NETSPARKER_API_TOKEN` | Invicti API Token |
| `NETSPARKER_ENDPOINT` | Invicti API base URL (e.g., `https://www.netsparkercloud.com`) |
| `NETSPARKER_WEBSITE_ID` | Target website ID in Invicti |
| `NETSPARKER_PROFILE_ID` | Scan profile ID in Invicti |

## Usage

The `dast-scan.yml` workflow runs:
- **Automatically** every day at 10 PM UTC on `main` (via cron schedule)
- **Manually** via `workflow_dispatch` with environment selection

The reusable workflows (`scan-base.yml`, `scan-netsparker.yml`) are called internally and should not be triggered directly.
