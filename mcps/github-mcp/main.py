"""GitHub MCP Server - Interact with GitHub via the REST API v3."""

import os
import json
import base64
import subprocess
import urllib.request as urllib_request
import urllib.parse as urllib_parse
import urllib.error as urllib_error
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("GitHub - opencode")

API_BASE = "https://api.github.com"
FILE_CONTENT_CAP = 100_000


def get_token():
    """Resolve GITHUB_TOKEN from env, falling back to `gh auth token`."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        token = out.stdout.strip()
        if out.returncode == 0 and token:
            return token
    except Exception:
        pass
    return None


def gh_api(method, path, body=None, token=None):
    """Call the GitHub REST API. Raises RuntimeError on non-2xx responses."""
    token = token or get_token()
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set and `gh auth token` fallback failed")

    url = path if path.startswith("http") else f"{API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib_request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "mcps-ai-github-mcp")
    if body is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib_request.urlopen(req, timeout=30) as r:
            raw = r.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8", errors="replace"))
    except urllib_error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8", errors="replace"))
            message = err_body.get("message", str(e))
            errors = err_body.get("errors")
            if errors:
                message = f"{message} ({json.dumps(errors)[:500]})"
        except Exception:
            message = str(e)
        raise RuntimeError(f"GitHub API {e.code}: {message}") from e


def repo_brief(r):
    return {
        "full_name": r.get("full_name"),
        "description": r.get("description"),
        "private": r.get("private"),
        "fork": r.get("fork"),
        "language": r.get("language"),
        "stargazers_count": r.get("stargazers_count"),
        "forks_count": r.get("forks_count"),
        "open_issues_count": r.get("open_issues_count"),
        "default_branch": r.get("default_branch"),
        "html_url": r.get("html_url"),
        "updated_at": r.get("updated_at"),
    }


def issue_brief(i):
    return {
        "number": i.get("number"),
        "title": i.get("title"),
        "state": i.get("state"),
        "user": (i.get("user") or {}).get("login"),
        "labels": [l.get("name") for l in i.get("labels", [])],
        "comments": i.get("comments"),
        "created_at": i.get("created_at"),
        "updated_at": i.get("updated_at"),
        "html_url": i.get("html_url"),
    }


def pr_brief(p):
    return {
        "number": p.get("number"),
        "title": p.get("title"),
        "state": p.get("state"),
        "draft": p.get("draft"),
        "user": (p.get("user") or {}).get("login"),
        "head": (p.get("head") or {}).get("ref"),
        "base": (p.get("base") or {}).get("ref"),
        "merged": p.get("merged"),
        "mergeable": p.get("mergeable"),
        "created_at": p.get("created_at"),
        "updated_at": p.get("updated_at"),
        "html_url": p.get("html_url"),
    }


def release_brief(r):
    return {
        "id": r.get("id"),
        "tag_name": r.get("tag_name"),
        "name": r.get("name"),
        "draft": r.get("draft"),
        "prerelease": r.get("prerelease"),
        "author": (r.get("author") or {}).get("login"),
        "published_at": r.get("published_at"),
        "html_url": r.get("html_url"),
        "body": (r.get("body") or "")[:2000],
    }


@mcp.tool
async def gh_repo_info(owner: str, repo: str):
    """Get full metadata for a GitHub repository."""
    try:
        r = gh_api("GET", f"/repos/{owner}/{repo}")
        return {
            "full_name": r.get("full_name"),
            "description": r.get("description"),
            "private": r.get("private"),
            "fork": r.get("fork"),
            "archived": r.get("archived"),
            "language": r.get("language"),
            "topics": r.get("topics", []),
            "stargazers_count": r.get("stargazers_count"),
            "watchers_count": r.get("watchers_count"),
            "forks_count": r.get("forks_count"),
            "open_issues_count": r.get("open_issues_count"),
            "size": r.get("size"),
            "default_branch": r.get("default_branch"),
            "license": (r.get("license") or {}).get("spdx_id"),
            "owner": (r.get("owner") or {}).get("login"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
            "pushed_at": r.get("pushed_at"),
            "html_url": r.get("html_url"),
            "clone_url": r.get("clone_url"),
        }
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo}


@mcp.tool
async def gh_list_repos(owner: str, repo_type: str = "owner", limit: int = 10):
    """List repositories for a user/org. repo_type: owner|org|user."""
    try:
        limit = max(1, min(int(limit), 100))
        if repo_type == "org":
            path = f"/orgs/{owner}/repos?per_page={limit}&sort=updated"
        elif repo_type in ("owner", "user"):
            path = f"/users/{owner}/repos?per_page={limit}&sort=updated&type=owner"
        else:
            return {"error": f"Invalid repo_type: {repo_type} (expected owner|org|user)", "owner": owner}
        repos = gh_api("GET", path)
        return {"owner": owner, "repo_type": repo_type, "count": len(repos), "repos": [repo_brief(r) for r in repos]}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo_type": repo_type}


@mcp.tool
async def gh_get_file(owner: str, repo: str, path: str, ref: str = "HEAD"):
    """Get a file's contents from a repository (decoded from base64)."""
    try:
        q = urllib_parse.urlencode({"ref": ref}) if ref and ref != "HEAD" else ""
        api_path = f"/repos/{owner}/{repo}/contents/{urllib_parse.quote(path)}"
        if q:
            api_path = f"{api_path}?{q}"
        data = gh_api("GET", api_path)
        if isinstance(data, list):
            return {"owner": owner, "repo": repo, "path": path, "type": "dir",
                    "entries": [{"name": e.get("name"), "type": e.get("type"), "path": e.get("path"), "size": e.get("size")} for e in data]}
        content_b64 = (data.get("content") or "").replace("\n", "")
        try:
            content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception:
            content = "[Unable to decode content]"
        truncated = len(content) > FILE_CONTENT_CAP
        return {
            "owner": owner,
            "repo": repo,
            "path": data.get("path"),
            "ref": ref,
            "sha": data.get("sha"),
            "size": data.get("size"),
            "encoding": data.get("encoding"),
            "content": content[:FILE_CONTENT_CAP],
            "truncated": truncated,
            "html_url": data.get("html_url"),
        }
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "path": path, "ref": ref}


@mcp.tool
async def gh_list_issues(owner: str, repo: str, state: str = "open", limit: int = 10):
    """List issues in a repository (pull requests are filtered out)."""
    try:
        limit = max(1, min(int(limit), 100))
        issues = gh_api("GET", f"/repos/{owner}/{repo}/issues?state={urllib_parse.quote(state)}&per_page={limit}")
        issues = [i for i in issues if "pull_request" not in i]
        return {"owner": owner, "repo": repo, "state": state, "count": len(issues), "issues": [issue_brief(i) for i in issues]}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo}


@mcp.tool
async def gh_get_issue(owner: str, repo: str, issue_number: int):
    """Get a single issue by number."""
    try:
        i = gh_api("GET", f"/repos/{owner}/{repo}/issues/{int(issue_number)}")
        result = issue_brief(i)
        result.update({
            "body": (i.get("body") or "")[:10000],
            "assignees": [a.get("login") for a in i.get("assignees", [])],
            "milestone": (i.get("milestone") or {}).get("title"),
            "is_pull_request": "pull_request" in i,
        })
        return result
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "issue_number": issue_number}


@mcp.tool
async def gh_create_issue(owner: str, repo: str, title: str, body: str = "", labels: str = ""):
    """Create a new issue. labels is a comma-separated string."""
    try:
        payload = {"title": title, "body": body}
        label_list = [l.strip() for l in labels.split(",") if l.strip()]
        if label_list:
            payload["labels"] = label_list
        i = gh_api("POST", f"/repos/{owner}/{repo}/issues", payload)
        return {"created": True, **issue_brief(i)}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "title": title}


@mcp.tool
async def gh_comment_issue(owner: str, repo: str, issue_number: int, body: str):
    """Add a comment to an issue or pull request."""
    try:
        c = gh_api("POST", f"/repos/{owner}/{repo}/issues/{int(issue_number)}/comments", {"body": body})
        return {
            "created": True,
            "id": c.get("id"),
            "issue_number": int(issue_number),
            "user": (c.get("user") or {}).get("login"),
            "created_at": c.get("created_at"),
            "html_url": c.get("html_url"),
        }
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "issue_number": issue_number}


@mcp.tool
async def gh_list_prs(owner: str, repo: str, state: str = "open", limit: int = 10):
    """List pull requests in a repository."""
    try:
        limit = max(1, min(int(limit), 100))
        prs = gh_api("GET", f"/repos/{owner}/{repo}/pulls?state={urllib_parse.quote(state)}&per_page={limit}")
        return {"owner": owner, "repo": repo, "state": state, "count": len(prs), "pull_requests": [pr_brief(p) for p in prs]}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo}


@mcp.tool
async def gh_get_pr(owner: str, repo: str, pr_number: int):
    """Get a single pull request by number."""
    try:
        p = gh_api("GET", f"/repos/{owner}/{repo}/pulls/{int(pr_number)}")
        result = pr_brief(p)
        result.update({
            "body": (p.get("body") or "")[:10000],
            "additions": p.get("additions"),
            "deletions": p.get("deletions"),
            "changed_files": p.get("changed_files"),
            "commits": p.get("commits"),
            "mergeable_state": p.get("mergeable_state"),
            "merged_at": p.get("merged_at"),
            "merged_by": (p.get("merged_by") or {}).get("login"),
            "labels": [l.get("name") for l in p.get("labels", [])],
        })
        return result
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "pr_number": pr_number}


@mcp.tool
async def gh_create_pr(owner: str, repo: str, title: str, head: str, base: str = "main", body: str = ""):
    """Create a pull request from head branch into base branch."""
    try:
        p = gh_api("POST", f"/repos/{owner}/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})
        return {"created": True, **pr_brief(p)}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "title": title, "head": head, "base": base}


@mcp.tool
async def gh_merge_pr(owner: str, repo: str, pr_number: int, merge_method: str = "merge"):
    """Merge a pull request. merge_method: merge|squash|rebase."""
    try:
        if merge_method not in ("merge", "squash", "rebase"):
            return {"error": f"Invalid merge_method: {merge_method} (expected merge|squash|rebase)",
                    "owner": owner, "repo": repo, "pr_number": pr_number}
        result = gh_api("PUT", f"/repos/{owner}/{repo}/pulls/{int(pr_number)}/merge", {"merge_method": merge_method})
        return {
            "merged": result.get("merged", True),
            "message": result.get("message"),
            "sha": result.get("sha"),
            "merge_method": merge_method,
            "owner": owner,
            "repo": repo,
            "pr_number": int(pr_number),
        }
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo, "pr_number": pr_number}


@mcp.tool
async def gh_search_repos(query: str, limit: int = 10):
    """Search repositories on GitHub."""
    try:
        limit = max(1, min(int(limit), 100))
        q = urllib_parse.quote(query)
        data = gh_api("GET", f"/search/repositories?q={q}&per_page={limit}")
        items = data.get("items", [])
        return {"query": query, "total_count": data.get("total_count"), "count": len(items),
                "repositories": [repo_brief(r) for r in items]}
    except Exception as e:
        return {"error": str(e), "query": query}


@mcp.tool
async def gh_search_issues(query: str, limit: int = 10):
    """Search issues and pull requests via /search/issues."""
    try:
        limit = max(1, min(int(limit), 100))
        q = urllib_parse.quote(query)
        data = gh_api("GET", f"/search/issues?q={q}&per_page={limit}")
        items = data.get("items", [])
        results = []
        for i in items:
            brief = issue_brief(i)
            brief["is_pull_request"] = "pull_request" in i
            results.append(brief)
        return {"query": query, "total_count": data.get("total_count"), "count": len(results), "issues": results}
    except Exception as e:
        return {"error": str(e), "query": query}


@mcp.tool
async def gh_list_releases(owner: str, repo: str, limit: int = 10):
    """List releases for a repository."""
    try:
        limit = max(1, min(int(limit), 100))
        releases = gh_api("GET", f"/repos/{owner}/{repo}/releases?per_page={limit}")
        return {"owner": owner, "repo": repo, "count": len(releases), "releases": [release_brief(r) for r in releases]}
    except Exception as e:
        return {"error": str(e), "owner": owner, "repo": repo}


@mcp.tool
async def gh_create_gist(description: str, filename: str, content: str, public: bool = False):
    """Create a gist with a single file."""
    try:
        payload = {
            "description": description,
            "public": bool(public),
            "files": {filename: {"content": content}},
        }
        g = gh_api("POST", "/gists", payload)
        return {
            "created": True,
            "id": g.get("id"),
            "description": g.get("description"),
            "public": g.get("public"),
            "files": list((g.get("files") or {}).keys()),
            "html_url": g.get("html_url"),
            "created_at": g.get("created_at"),
        }
    except Exception as e:
        return {"error": str(e), "description": description, "filename": filename}


@mcp.tool
async def gh_list_gists(limit: int = 10):
    """List gists for the authenticated user."""
    try:
        limit = max(1, min(int(limit), 100))
        gists = gh_api("GET", f"/gists?per_page={limit}")
        return {
            "count": len(gists),
            "gists": [{
                "id": g.get("id"),
                "description": g.get("description"),
                "public": g.get("public"),
                "files": list((g.get("files") or {}).keys()),
                "created_at": g.get("created_at"),
                "updated_at": g.get("updated_at"),
                "html_url": g.get("html_url"),
            } for g in gists],
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == '__main__':
    mcp.run(transport="stdio")
