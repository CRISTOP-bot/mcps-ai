# github-mcp

MCP server for the GitHub REST API v3. Built with FastMCP; uses stdlib `urllib` for HTTP (no requests/httpx).

## Setup

1. Create a Personal Access Token (PAT) at <https://github.com/settings/tokens>:
   - Click **Generate new token** (classic) or a fine-grained token.
   - For a classic token, grant the **`repo`** scope (full repository access) and the **`gist`** scope (create/list gists).
   - For a fine-grained token, grant repository permissions: Contents (read/write), Issues (read/write), Pull requests (read/write), and Gists if supported.
2. Provide the token via `.env` or environment variable:
   - Copy `.env.example` to `.env` and set `GITHUB_TOKEN=ghp_...`, or
   - `export GITHUB_TOKEN=ghp_...`
   - If `GITHUB_TOKEN` is not set, the server falls back to `gh auth token` (requires the GitHub CLI, authenticated). If both fail, tools return an error dict instead of raising.
3. Install and run:
   ```bash
   uv sync
   uv run python main.py
   ```
   The server speaks MCP over stdio.

## Tools

| Tool | Description |
| --- | --- |
| `gh_repo_info` | Get full metadata for a repository |
| `gh_list_repos` | List repositories for a user/org (repo_type: owner\|org\|user) |
| `gh_get_file` | Get a file's contents from a repo (decoded from base64) |
| `gh_list_issues` | List issues in a repo (PRs filtered out) |
| `gh_get_issue` | Get a single issue by number |
| `gh_create_issue` | Create a new issue (labels comma-separated) |
| `gh_comment_issue` | Add a comment to an issue or PR |
| `gh_list_prs` | List pull requests in a repo |
| `gh_get_pr` | Get a single pull request by number |
| `gh_create_pr` | Create a pull request from head into base |
| `gh_merge_pr` | Merge a PR (merge_method: merge\|squash\|rebase) |
| `gh_search_repos` | Search repositories |
| `gh_search_issues` | Search issues and PRs via /search/issues |
| `gh_list_releases` | List releases for a repo |
| `gh_create_gist` | Create a gist with a single file |
| `gh_list_gists` | List gists for the authenticated user |

## Notes

- All tools return compact dicts and never raise; on failure they return `{"error": ...}` with context.
- File content is capped at 100,000 chars.
- Non-2xx GitHub responses surface the API's `message` field in the error string.
