# Contributing to MCPs for AI Agents

## Structure

```
mcps/          # Canonical MCP servers (single source of truth)
agents/        # Per-agent setup docs (no duplicated code)
cli/           # mcps-ai npm package
```

## Adding a new MCP

1. Create `mcps/<name>-mcp/main.py` (FastMCP server)
2. Add `pyproject.toml` with dependencies
3. Add tests in `mcps/<name>-mcp/tests/`
4. Add import test to `.github/workflows/ci.yml`
5. Update `install.md` and `README.md`
6. Update `cli/src/install.js` `getMcpConfigs()` to include the new MCP

## Adding a new agent

1. Create `agents/<agent>/README.md` with MCP config block
2. Add config writer in `cli/src/agents.js`
3. Add detection logic (path or command check)

## Testing

```bash
uv sync
uv run pytest tests/ -v
```

## Code style

- Python 3.10+
- Type hints where practical
- No external dependencies unless necessary
- Handle errors gracefully (return `{"error": "..."}` instead of raising)
