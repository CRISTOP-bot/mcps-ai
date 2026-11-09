---
name: use-github
description: Usar GitHub desde el agente — repos, issues, PRs, búsqueda, releases, gists. Se activa cuando el usuario pide GitHub.
---

# Skill: Usar GitHub

## Herramientas (namespace `github`)
- `gh_repo_info(owner, repo)` / `gh_list_repos(owner, repo_type, limit)`
- `gh_get_file(owner, repo, path, ref)` — leer archivos decodificados
- `gh_list_issues` / `gh_get_issue` / `gh_create_issue` / `gh_comment_issue`
- `gh_list_prs` / `gh_get_pr` / `gh_create_pr` / `gh_merge_pr(merge|squash|rebase)`
- `gh_search_repos(query)` / `gh_search_issues(query)`
- `gh_list_releases(owner, repo)` / `gh_create_gist` / `gh_list_gists`

## Reglas
1. Token: `GITHUB_TOKEN` (o fallback a `gh auth token`). Scopes: `repo`, `gist`.
2. Confirmar antes de crear issues/PRs/gists públicos o hacer merge.
3. Para buscar código usar `gh_search_issues("repo:owner/name is:issue ...")`.
4. No comentar en issues sin confirmación del usuario.
