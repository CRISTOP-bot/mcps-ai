# Orchestrator MCP

Multi-agent coordination: a **Director** dispatches parallel workers (OpenCode sessions), collects their outputs, and synthesizes one final answer. Agents communicate through a shared blackboard + message log.

## Concepts

- **Persistent agents** — created with `orchestra_create_agent(name, role)`; they keep their session and memory across calls (`orchestra_send`, `orchestra_broadcast`).
- **Director runs** — one-shot teamwork on a goal: `orchestra_director_run(goal, roles="researcher,coder,reviewer")` → workers answer in parallel → Director synthesizes.
- **Blackboard** — shared key/value memory all agents can read/write mid-task.
- **Message log** — full transcript of what every agent said (`orchestra_messages`).

## Tools (12)

| Tool | Qué hace |
|------|----------|
| `orchestra_status` | OpenCode server health + counts |
| `orchestra_create_agent(name, role, system_prompt, model_id)` | Create persistent agent |
| `orchestra_list_agents` | List agents |
| `orchestra_delete_agent(agent_id)` | Delete agent + session |
| `orchestra_send(agent_id, message, timeout)` | Send & wait for reply |
| `orchestra_broadcast(message, agent_ids)` | Same message to many agents in parallel |
| `orchestra_director_run(goal, roles, timeout)` | Fan-out to workers → Director synthesizes |
| `orchestra_blackboard_read/write/list/delete` | Shared memory |
| `orchestra_messages(limit, run_id)` | Transcript; filter by run |
| `orchestra_runs(limit)` | Recent director runs |
| `orchestra_interrupt(agent_id)` | Cancel generation |

## Built-in worker personas

`researcher`, `analyst`, `coder`, `reviewer`, `critic`, `planner`, `writer` — anything else gets a generic persona.

## Setup

```bash
cd mcps/orchestrator-mcp
cp .env.example .env   # fill AI_PASSWORD (same one your telegram worker uses)
uv sync
```

Requires a running OpenCode Server (127.0.0.1:4096) — same one the Telegram worker uses.

## Example

```python
orchestra_director_run(
    "Design a rate limiter for our API",
    roles="analyst,coder,reviewer"
)
```
