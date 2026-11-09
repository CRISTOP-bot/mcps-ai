"""Orchestrator MCP - Coordinate multiple AI agents as a team under a director.

Agents here are concurrent sessions on the OpenCode Server (127.0.0.1:4096).
They communicate through a shared blackboard + message log (SQLite), and one
session acts as the Director who dispatches, collects and synthesizes.
"""
import asyncio
import json
import time
import uuid
import logging

from fastmcp import FastMCP
from dotenv import load_dotenv

from config import REQUEST_TIMEOUT
import store
from ai_client import AIClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestrator-mcp")

mcp = FastMCP("Orchestrator - opencode")
client = AIClient()

ROLE_PROMPTS = {
    "researcher": "You are the Researcher on an AI team. Find the key facts, options and prior art for the goal. Be concise and cite uncertainty explicitly.",
    "analyst": "You are the Analyst on an AI team. Break the goal into structure: assumptions, risks, dependencies, decision points.",
    "coder": "You are the Coder on an AI team. Propose a concrete implementation: file layout, key code, libraries. Working code beats prose.",
    "reviewer": "You are the Reviewer on an AI team. Find flaws, edge cases, security issues and simpler alternatives in what a teammate would propose.",
    "critic": "You are the Critic on an AI team. Argue against the obvious solution: what breaks, what's over-engineered, what's missing?",
    "planner": "You are the Planner on an AI team. Produce a step-by-step execution plan with milestones and verification points.",
    "writer": "You are the Writer on an AI team. Draft the final human-readable output (docs, message, README) as if for an end user.",
}


def _parse_roles(roles):
    return [r.strip().lower() for r in roles.split(",") if r.strip()]


def _worker_prompt(role, goal):
    persona = ROLE_PROMPTS.get(role, f"You are the '{role}' on an AI team. Contribute your {role} perspective.")
    return (
        f"{persona}\n\nGoal: {goal}\n\n"
        "Answer in plain text (no markdown). Be concrete. Max ~250 words. "
        "If the goal is ambiguous, state your assumptions and proceed."
    )


async def _worker(role, goal, run_id, timeout):
    started = time.time()
    try:
        session = await client.create_session(title=f"orchestra-{role}-{run_id[:6]}")
        session_id = session.get("id") or session.get("sessionID") or session.get("session_id")
        await client.switch_model(session_id)
        reply = await client.full_request(session_id, _worker_prompt(role, goal), timeout=timeout)
        store.log_message(run_id, f"worker-{role}", role, reply)
        return role, {"reply": reply, "session_id": session_id, "elapsed": round(time.time() - started, 1)}
    except Exception as e:
        err = f"worker error: {e}"
        store.log_message(run_id, f"worker-{role}", role, err)
        return role, {"reply": err, "session_id": None, "elapsed": round(time.time() - started, 1)}


@mcp.tool
async def orchestra_status():
    """Health check + counts: agents, runs, blackboard entries, messages."""
    ok, info = await client.health_check()
    return {
        "opencode_server": "up" if ok else f"down: {info}",
        **store.stats(),
        "timeout_seconds": REQUEST_TIMEOUT,
    }


@mcp.tool
async def orchestra_create_agent(name: str, role: str, system_prompt: str = "", model_id: str = ""):
    """Create a persistent AI agent (OpenCode session) with a role. Returns agent_id and session_id."""
    try:
        session = await client.create_session(title=f"agent:{name}")
        session_id = session.get("id") or session.get("sessionID") or session.get("session_id")
        if model_id:
            await client.switch_model(session_id, model_id=model_id)
        agent_id = store.add_agent(name, role, session_id, model_id=model_id, system_prompt=system_prompt)
        store.log_message("-", name, role, f"Agent created (session {session_id})")
        return {"agent_id": agent_id, "session_id": session_id, "name": name, "role": role}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def orchestra_list_agents():
    """List registered agents (id, name, role, session_id, activity)."""
    try:
        return {"agents": store.list_agents()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def orchestra_delete_agent(agent_id: str):
    """Delete an agent: remove its OpenCode session AND its registry record."""
    try:
        agent = store.get_agent(agent_id)
        if not agent:
            return {"error": f"no agent with id {agent_id}"}
        await client.delete_session(agent["session_id"])
        store.delete_agent(agent_id)
        return {"status": "deleted", "agent_id": agent_id, "name": agent["name"]}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def orchestra_send(agent_id: str, message: str, timeout: float = 300):
    """Send a message to a persistent agent and wait for its reply (blocks). timeout=0 means no limit."""
    agent = store.get_agent(agent_id)
    if not agent:
        return {"error": f"no agent with id {agent_id}"}
    try:
        payload = message
        if agent.get("system_prompt"):
            payload = f"{agent['system_prompt']}\n\n{message}"
        reply = await client.full_request(agent["session_id"], payload, timeout=timeout)
        store.touch_agent(agent_id)
        store.log_message("-", agent["name"], agent["role"], reply)
        return {"agent": agent["name"], "role": agent["role"], "reply": reply}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def orchestra_broadcast(message: str, agent_ids: str = ""):
    """Send the same message to several agents in PARALLEL. agent_ids='id1,id2' or empty for ALL agents."""
    try:
        agents = store.list_agents()
        wanted = [a for a in agent_ids.split(",") if a.strip()]
        if wanted:
            agents = [a for a in agents if a["id"] in wanted]
        if not agents:
            return {"error": "no agents matched", "configured_ids": [a["id"] for a in store.list_agents()]}

        async def one(a):
            agent = store.get_agent(a["id"])
            payload = f"{agent['system_prompt']}\n\n{message}" if agent.get("system_prompt") else message
            reply = await client.full_request(agent["session_id"], payload, timeout=300)
            store.touch_agent(a["id"])
            store.log_message("broadcast", a["name"], a["role"], reply)
            return a["name"], reply

        results = await asyncio.gather(*(one(a) for a in agents), return_exceptions=True)
        out = {}
        for a, r in zip(agents, results):
            out[a["name"]] = f"worker error: {r}" if isinstance(r, Exception) else r[1]
        return {"replies": out, "count": len(out)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def orchestra_director_run(goal: str, roles: str = "researcher,coder,reviewer", timeout: float = 0):
    """THE main tool: goal -> N worker agents in PARALLEL -> Director synthesizes one final answer.

    roles: comma-separated roles for temporary workers (known personas: researcher, analyst, coder, reviewer, critic, planner, writer; anything else gets a generic persona).
    timeout: per-worker wait in seconds (0 = no limit).
    """
    role_list = _parse_roles(roles)
    if not role_list:
        return {"error": "no roles parsed from 'roles' argument"}
    if timeout == 0:
        timeout = None

    run_id = store.create_run(goal)
    store.log_message(run_id, "director", "director", f"Goal received: {goal}")
    logger.info("director_run %s: goal=%s roles=%s", run_id, goal[:80], role_list)

    # Phase 1: fan-out workers in parallel
    results = await asyncio.gather(*(_worker(r, goal, run_id, timeout) for r in role_list))
    workers = {role: data for role, data in results}

    worker_block = "\n\n".join(
        f"--- {role.upper()} (elapsed {data['elapsed']}s) ---\n{data['reply']}"
        for role, data in workers.items()
    )

    # Phase 2: director synthesizes
    director_prompt = (
        "You are the Director of an AI team. Your job is to synthesize the workers' output into ONE final, actionable answer.\n\n"
        f"GOAL: {goal}\n\n"
        f"WORKER OUTPUTS:\n{worker_block}\n\n"
        "Produce the final answer for the user: concrete, ordered, no meta-commentary. "
        "If workers disagree, state the strongest option and why. Plain text, no markdown."
    )
    try:
        director_session = await client.create_session(title=f"orchestra-director-{run_id[:6]}")
        director_sid = director_session.get("id") or director_session.get("sessionID") or director_session.get("session_id")
        await client.switch_model(director_sid)
        synthesis = await client.full_request(director_sid, director_prompt, timeout=timeout)
    except Exception as e:
        synthesis = f"director error: {e}"

    store.log_message(run_id, "director", "director", synthesis)
    store.finish_run(run_id, {r: w for r, w in workers.items()}, "done", synthesis)
    store.blackboard_write(f"run:{run_id}", json.dumps({"goal": goal, "workers": workers, "synthesis": synthesis}, ensure_ascii=False))

    return {
        "run_id": run_id,
        "goal": goal,
        "workers": workers,
        "director": synthesis,
    }


@mcp.tool
async def orchestra_blackboard_read(key: str):
    """Read a shared blackboard entry by key."""
    entry = store.blackboard_read(key)
    return entry if entry else {"error": f"no key '{key}'", "keys": [b["key"] for b in store.blackboard_list()]}


@mcp.tool
async def orchestra_blackboard_write(key: str, value: str):
    """Write/overwrite a shared blackboard entry. Agents read these mid-task to coordinate."""
    store.blackboard_write(key, value)
    store.log_message("-", "blackboard", "system", f"wrote '{key}'")
    return {"status": "ok", "key": key}


@mcp.tool
async def orchestra_blackboard_list():
    """List all blackboard keys (shared memory index)."""
    return {"entries": store.blackboard_list()}


@mcp.tool
async def orchestra_blackboard_delete(key: str):
    """Delete a blackboard entry."""
    store.blackboard_delete(key)
    return {"status": "deleted", "key": key}


@mcp.tool
async def orchestra_messages(limit: int = 20, run_id: str = ""):
    """Shared message log: what each agent said (most recent first). Filter by run_id to see one orchestration."""
    limit = max(1, min(limit, 200))
    return {"messages": store.get_messages(limit=limit, run_id=run_id)}


@mcp.tool
async def orchestra_runs(limit: int = 10):
    """List recent director runs (id, goal, status, timing)."""
    return {"runs": store.list_runs(limit=max(1, min(limit, 100)))}


@mcp.tool
async def orchestra_interrupt(agent_id: str):
    """Interrupt the current generation of a persistent agent."""
    agent = store.get_agent(agent_id)
    if not agent:
        return {"error": f"no agent with id {agent_id}"}
    ok = await client.interrupt(agent["session_id"])
    return {"status": "interrupted" if ok else "no active generation", "agent": agent["name"]}


if __name__ == "__main__":
    mcp.run(transport="stdio")
