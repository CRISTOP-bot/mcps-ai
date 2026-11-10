// Agent detection
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const HOME = os.homedir();

function commandExists(cmd) {
  try {
    execSync(`which ${cmd} 2>/dev/null`, { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

function dirExists(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

function fileExists(p) {
  try { return fs.statSync(p).isFile(); } catch { return false; }
}

function dirExists(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

// Merge: keep existing working server configs; only fill in missing ones,
// and preserve user-set env vars (never overwrite with empty values).
function mergeServers(existing, incoming) {
  const merged = { ...(existing || {}) };
  for (const [name, cfg] of Object.entries(incoming || {})) {
    if (merged[name]) {
      // Keep existing command if its directory exists, otherwise take incoming
      const dirIdx = merged[name].command ? merged[name].command.indexOf('--directory') : -1;
      const dir = dirIdx >= 0 ? merged[name].command[dirIdx + 1] : null;
      const dirOk = dir && dirExists(dir);
      merged[name] = {
        ...merged[name],
        ...(dirOk ? {} : { command: cfg.command }),
        // Preserve existing environment entries that are non-empty
        environment: { ...(cfg.environment || {}), ...(merged[name].environment || {}) },
      };
    } else {
      merged[name] = cfg;
    }
  }
  return merged;
}

const AGENTS = [
  {
    id: 'opencode',
    name: 'OpenCode',
    detect: () => dirExists(path.join(HOME, '.config/opencode')) || commandExists('opencode'),
    configPath: () => path.join(HOME, '.config/opencode/opencode.json'),
    writeConfig(config) {
      const p = path.join(HOME, '.config/opencode/opencode.json');
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcp = current.mcp || {};
      current.mcp.servers = mergeServers(current.mcp.servers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'claude',
    name: 'Claude Desktop',
    detect: () => {
      if (process.platform === 'darwin') {
        return fileExists(path.join(HOME, 'Library/Application Support/Claude/claude_desktop_config.json'));
      }
      return fileExists(path.join(HOME, '.config/claude/claude_desktop_config.json'));
    },
    configPath: () => process.platform === 'darwin'
      ? path.join(HOME, 'Library/Application Support/Claude/claude_desktop_config.json')
      : path.join(HOME, '.config/claude/claude_desktop_config.json'),
    writeConfig(config) {
      const p = this.configPath();
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcpServers = mergeServers(current.mcpServers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'claude-code',
    name: 'Claude Code',
    detect: () => commandExists('claude') || fileExists(path.join(HOME, '.claude/.mcp.json')) || fileExists(path.join(process.cwd(), '.mcp.json')),
    configPath: () => path.join(HOME, '.claude/.mcp.json'),
    writeConfig(config) {
      const p = path.join(HOME, '.claude/.mcp.json');
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcpServers = mergeServers(current.mcpServers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'cursor',
    name: 'Cursor',
    detect: () => fileExists(path.join(process.cwd(), '.cursor/mcp.json')) || fileExists(path.join(HOME, '.cursor/mcp.json')) || commandExists('cursor'),
    configPath: () => path.join(process.cwd(), '.cursor/mcp.json'),
    writeConfig(config) {
      const p = this.configPath();
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcpServers = mergeServers(current.mcpServers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'kiro',
    name: 'Kiro',
    detect: () => dirExists(path.join(HOME, '.kiro')) || commandExists('kiro'),
    configPath: () => path.join(HOME, '.kiro/settings/mcp.json'),
    writeConfig(config) {
      const p = this.configPath();
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcpServers = mergeServers(current.mcpServers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'windsurf',
    name: 'Windsurf',
    detect: () => dirExists(path.join(HOME, '.codeium')) || fileExists(path.join(HOME, '.codeium/windsurf/mcp_config.json')),
    configPath: () => path.join(HOME, '.codeium/windsurf/mcp_config.json'),
    writeConfig(config) {
      const p = this.configPath();
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      current.mcpServers = mergeServers(current.mcpServers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
  {
    id: 'openclaw',
    name: 'OpenClaw',
    detect: () => dirExists(path.join(HOME, '.openclaw')) || commandExists('openclaw') || fileExists(path.join(HOME, '.openclaw/config.json')),
    configPath: () => path.join(HOME, '.openclaw/config.json'),
    writeConfig(config) {
      const p = this.configPath();
      let current = {};
      if (fileExists(p)) {
        try { current = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { current = {}; }
      }
      // OpenClaw uses mcp.servers structure
      current.mcp = current.mcp || {};
      current.mcp.servers = mergeServers(current.mcp.servers, config);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(current, null, 2));
      try { fs.chmodSync(p, 0o600); } catch {}
    },
  },
];

function detectAgents() {
  return AGENTS.filter(a => {
    try { return a.detect(); } catch { return false; }
  });
}

module.exports = { AGENTS, detectAgents, _test: { mergeServers } };
