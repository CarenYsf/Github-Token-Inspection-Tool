# GitHub Token Inspection Tool

A small command-line tool that inspects a GitHub API token. It validates the token, identifies the associated GitHub account, and reports useful metadata such as token scopes and API rate limits. The tool always returns a machine-readable JSON output.

## Features
- Validate a GitHub API token
- Identify the GitHub user linked to the token
- Extract token scopes from response headers
- Report API rate-limit information
- Defensive error handling
- No token logging or storage

## How It Works
The tool performs an authenticated request to the GitHub REST API endpoint `GET https://api.github.com/user`. A successful response confirms the token’s validity and returns user information. Failures are reported in a structured JSON format.

## Requirements
- Python 3.8+
- `requests` library

```bash
pip install requests
