// Install / update logic
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
const readline = require('readline');
const https = require('https');

const INSTALL_DIR = path.join(os.homedir(), '.mcps-ai');
const REPO_DIR = path.join(INSTALL_DIR, 'repo');
const REPO_URL = 'https://github.com/CRISTOP-bot/mcps-ai.git';

function run(cmd, cwd) {
  return execSync(cmd, { cwd, stdio: 'inherit' });
}

function fileExists(p) {
  try { return fs.statSync(p).isFile(); } catch { return false; }
}

function backupConfig(p) {
  if (fileExists(p)) {
    const backup = p + '.bak.' + Date.now();
    fs.copyFileSync(p, backup);
    return backup;
  }
  return null;
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

function dirExists(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, answer => { rl.close(); resolve(answer.trim()); }));
}

function askYesNo(question, defaultYes = true) {
  const suffix = defaultYes ? " [Y/n]: " : " [y/N]: ";
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question + suffix, answer => {
    rl.close();
    const a = answer.trim().toLowerCase();
    if (!a) return resolve(defaultYes);
    resolve(a === 'y' || a === 'yes');
  }));
}

function ensureRepo(sourcePath) {
  if (sourcePath) {
    // Use local source path
    const dest = path.join(INSTALL_DIR, 'repo');
    if (!dirExists(dest)) {
      fs.mkdirSync(dest, { recursive: true });
      // Copy local source
      run(`cp -r "${sourcePath}/." "${dest}"`);
    } else {
      // Update: git pull if it's a git repo, otherwise just leave it
      if (dirExists(path.join(dest, '.git'))) {
        try { run('git pull --ff-only', dest); } catch { console.log('Keeping existing install (git pull failed)'); }
      }
    }
    return dest;
  }

  if (dirExists(REPO_DIR)) {
    if (dirExists(path.join(REPO_DIR, '.git'))) {
      console.log('Updating existing installation...');
      try { run('git pull --ff-only', REPO_DIR); } catch { console.log('Update failed, keeping current version'); }
    }
    return REPO_DIR;
  }

  // Clone fresh
  fs.mkdirSync(INSTALL_DIR, { recursive: true });
  console.log('Cloning mcps-ai...');
  run(`git clone ${REPO_URL} ${REPO_DIR}`);
  return REPO_DIR;
}

function getMcpConfigs(agentId, repoDir) {
  // Returns MCP server config entries pointing at the canonical mcps/ directory
  const base = path.join(repoDir, 'mcps');
  const config = {};

  if (fileExists(path.join(base, 'telegram-mcp', 'main.py'))) {
    const tgEnv = process.env.TELEGRAM_BOT_TOKEN;
    config.telegram = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'telegram-mcp'), 'run', 'main.py'],
      env: tgEnv ? { TELEGRAM_BOT_TOKEN: tgEnv } : {},
    };
  }
  if (fileExists(path.join(base, 'whatsapp-mcp', 'whatsapp-mcp-server', 'main.py'))) {
    config.whatsapp = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'whatsapp-mcp', 'whatsapp-mcp-server'), 'run', 'main.py'],
    };
  }
  if (fileExists(path.join(base, 'minecraft-mcp', 'main.py'))) {
    config.minecraft = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'minecraft-mcp'), 'run', 'main.py'],
      env: {
        MC_HOST: 'localhost',
        MC_PORT: '25575',
        MC_RCON_PASSWORD: process.env.MC_RCON_PASSWORD || '',
        MC_PLAYER: process.env.MC_PLAYER || '',
      },
    };
  }
  if (fileExists(path.join(base, 'gmail-mcp', 'main.py'))) {
    config.gmail = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'gmail-mcp'), 'run', 'main.py'],
      env: {
        GMAIL_CREDENTIALS: path.join(base, 'gmail-mcp', 'credentials.json'),
        GMAIL_TOKEN: path.join(base, 'gmail-mcp', 'token.json'),
      },
    };
  }
  if (fileExists(path.join(base, 'filesystem-mcp', 'main.py'))) {
    config.filesystem = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'filesystem-mcp'), 'run', 'main.py'],
    };
  }
  if (fileExists(path.join(base, 'system-mcp', 'main.py'))) {
    config.system = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'system-mcp'), 'run', 'main.py'],
    };
  }
  if (fileExists(path.join(base, 'web-mcp', 'main.py'))) {
    config.web = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'web-mcp'), 'run', 'main.py'],
    };
  }
  if (fileExists(path.join(base, 'browser-mcp', 'main.py'))) {
    config.browser = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'browser-mcp'), 'run', 'main.py'],
    };
  }
  if (fileExists(path.join(base, 'github-mcp', 'main.py'))) {
    config.github = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'github-mcp'), 'run', 'main.py'],
      env: process.env.GITHUB_TOKEN ? { GITHUB_TOKEN: process.env.GITHUB_TOKEN } : {},
    };
  }
  if (fileExists(path.join(base, 'discord-mcp', 'main.py'))) {
    const env = {};
    if (process.env.DISCORD_BOT_TOKEN) env.DISCORD_BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;
    if (process.env.DISCORD_WEBHOOK_URL) env.DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;
    config.discord = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'discord-mcp'), 'run', 'main.py'],
      env,
    };
  }
  if (fileExists(path.join(base, 'spotify-mcp', 'main.py'))) {
    const env = {};
    if (process.env.SPOTIFY_CLIENT_ID) env.SPOTIFY_CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
    if (process.env.SPOTIFY_CLIENT_SECRET) env.SPOTIFY_CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
    if (process.env.SPOTIFY_REFRESH_TOKEN) env.SPOTIFY_REFRESH_TOKEN = process.env.SPOTIFY_REFRESH_TOKEN;
    config.spotify = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'spotify-mcp'), 'run', 'main.py'],
      env,
    };
  }
  if (fileExists(path.join(base, 'slack-mcp', 'main.py'))) {
    config.slack = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'slack-mcp'), 'run', 'main.py'],
      env: process.env.SLACK_BOT_TOKEN ? { SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN } : {},
    };
  }
  if (fileExists(path.join(base, 'notion-mcp', 'main.py'))) {
    config.notion = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'notion-mcp'), 'run', 'main.py'],
      env: process.env.NOTION_API_KEY ? { NOTION_API_KEY: process.env.NOTION_API_KEY } : {},
    };
  }
  if (fileExists(path.join(base, 'homeassistant-mcp', 'main.py'))) {
    const env = {};
    if (process.env.HA_URL) env.HA_URL = process.env.HA_URL;
    if (process.env.HA_TOKEN) env.HA_TOKEN = process.env.HA_TOKEN;
    config.homeassistant = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'homeassistant-mcp'), 'run', 'main.py'],
      env,
    };
  }
  return config;
}

function installMcpDependencies(repoDir, agentId) {
  // Canonical layout: all MCPs live in <repo>/mcps/<name>-mcp/
  const base = path.join(repoDir, 'mcps');
  if (!dirExists(base)) return;
  const uv = path.join(os.homedir(), '.local/bin/uv');
  const uvCmd = fileExists(uv) ? uv : 'uv';
  const mcpDirs = fs.readdirSync(base, { withFileTypes: true }).filter(d => d.isDirectory());
  for (const d of mcpDirs) {
    const mcpPath = path.join(base, d.name);
    if (fileExists(path.join(mcpPath, 'pyproject.toml'))) {
      console.log(`  Installing deps for ${d.name}...`);
      try {
        run(`${uvCmd} sync`, mcpPath);
      } catch (e) {
        console.log(`    (deps failed for ${d.name}, continuing)`);
      }
    } else if (fileExists(path.join(mcpPath, 'whatsapp-mcp-server', 'pyproject.toml'))) {
      console.log(`  Installing deps for whatsapp-mcp...`);
      try {
        run(`${uvCmd} sync`, path.join(mcpPath, 'whatsapp-mcp-server'));
      } catch (e) {
        console.log(`    (deps failed for whatsapp-mcp, continuing)`);
      }
    }
  }
}

// Write a .env file for an MCP, preserving any existing file unless the user opts in.
async function writeEnv(baseDir, mcpName, envLines) {
  const envPath = path.join(baseDir, mcpName, '.env');
  const content = envLines.join('\n') + '\n';
  if (fileExists(envPath)) {
    const overwrite = await askYesNo(`Ya existe .env para ${mcpName}. ¿Sobrescribir?`, false);
    if (!overwrite) {
      console.log(`  Manteniendo .env existente (${mcpName})`);
      return;
    }
  }
  fs.writeFileSync(envPath, content);
  console.log(`  .env creado para ${mcpName}`);
}

async function promptCredentials(repoDir, agentId, env) {
  const base = path.join(repoDir, 'mcps');
  if (!dirExists(base)) return;
  const envPath = path.join(base, 'telegram-mcp', '.env');

  console.log('\n=== Configuración de credenciales ===');
  console.log('Presiona Enter para saltar (usa valores por defecto)\n');

  // Telegram
  if (fileExists(path.join(base, 'telegram-mcp'))) {
    const token = await ask('TELEGRAM_BOT_TOKEN (de @BotFather): ');
    if (token) {
      const chatIds = await ask('TELEGRAM_ALLOWED_USERS (IDs separados por coma, ej: 123456789): ');
      const envContent = [
        `TELEGRAM_BOT_TOKEN=${token}`,
        `TELEGRAM_ALLOWED_USERS=${chatIds || ''}`,
        `AI_BASE_URL=http://127.0.0.1:4096`,
        `AI_PASSWORD=${process.env.AI_PASSWORD || ''}`,
        `AI_DIRECTORY=${os.homedir()}`,
        `DATABASE_PATH=./data/telegram.db`,
        `REQUEST_TIMEOUT=0`,
        `AI_MODEL_ID=deepseek-v4.1-flash-free`,
        `AI_MODEL_PROVIDER=opencode`,
        `AI_AUTH_USER=opencode`,
      ].join('\n');
      // Don't overwrite existing .env
      if (fileExists(envPath)) {
        const overwrite = await askYesNo('Ya existe .env para telegram-mcp. ¿Sobrescribir?', false);
        if (!overwrite) {
          console.log('  Manteniendo .env existente');
        } else {
          fs.writeFileSync(envPath, envContent + '\n');
          console.log('  .env actualizado');
        }
      } else {
        fs.writeFileSync(envPath, envContent + '\n');
        console.log('  .env creado');
      }
    }
  }

  // Minecraft
  if (fileExists(path.join(base, 'minecraft-mcp'))) {
    const host = await ask('MC_HOST [localhost]: ');
    const port = await ask('MC_PORT [25575]: ');
    const password = await ask('MC_RCON_PASSWORD (vacío = saltar): ');
    if (host || port || password) {
      const mcEnvPath = path.join(base, 'minecraft-mcp', '.env');
      const mcContent = [
        `MC_HOST=${host || 'localhost'}`,
        `MC_PORT=${port || '25575'}`,
        `MC_RCON_PASSWORD=${password}`,
        `MC_PLAYER=${process.env.MC_PLAYER || ''}`,
      ].join('\n');
      if (fileExists(mcEnvPath)) {
        const overwrite = await askYesNo('Ya existe .env para minecraft-mcp. ¿Sobrescribir?', false);
        if (!overwrite) {
          console.log('  Manteniendo .env existente');
        } else {
          fs.writeFileSync(mcEnvPath, mcContent + '\n');
          console.log('  .env actualizado');
        }
      } else {
        fs.writeFileSync(mcEnvPath, mcContent + '\n');
        console.log('  .env creado');
      }
    }
  }

  // GitHub
  if (fileExists(path.join(base, 'github-mcp'))) {
    const token = await ask('GITHUB_TOKEN (Enter = intentar `gh auth token` en tiempo de ejecución, o saltar): ');
    if (token) {
      await writeEnv(base, 'github-mcp', [`GITHUB_TOKEN=${token}`]);
    }
  }

  // Discord
  if (fileExists(path.join(base, 'discord-mcp'))) {
    const botToken = await ask('DISCORD_BOT_TOKEN (Enter = saltar): ');
    const webhook = await ask('DISCORD_WEBHOOK_URL (opcional, Enter = saltar): ');
    if (botToken || webhook) {
      const lines = [];
      if (botToken) lines.push(`DISCORD_BOT_TOKEN=${botToken}`);
      if (webhook) lines.push(`DISCORD_WEBHOOK_URL=${webhook}`);
      await writeEnv(base, 'discord-mcp', lines);
    }
  }

  // Spotify
  if (fileExists(path.join(base, 'spotify-mcp'))) {
    const cid = await ask('SPOTIFY_CLIENT_ID (Enter = saltar): ');
    if (cid) {
      const secret = await ask('SPOTIFY_CLIENT_SECRET: ');
      const refresh = await ask('SPOTIFY_REFRESH_TOKEN: ');
      await writeEnv(base, 'spotify-mcp', [
        `SPOTIFY_CLIENT_ID=${cid}`,
        `SPOTIFY_CLIENT_SECRET=${secret}`,
        `SPOTIFY_REFRESH_TOKEN=${refresh}`,
      ]);
    }
  }

  // Slack
  if (fileExists(path.join(base, 'slack-mcp'))) {
    const token = await ask('SLACK_BOT_TOKEN (xoxb-..., Enter = saltar): ');
    if (token) {
      await writeEnv(base, 'slack-mcp', [`SLACK_BOT_TOKEN=${token}`]);
    }
  }

  // Notion
  if (fileExists(path.join(base, 'notion-mcp'))) {
    const key = await ask('NOTION_API_KEY (ntn_/secret_..., Enter = saltar): ');
    if (key) {
      await writeEnv(base, 'notion-mcp', [`NOTION_API_KEY=${key}`]);
    }
  }

  // Home Assistant
  if (fileExists(path.join(base, 'homeassistant-mcp'))) {
    const url = await ask('HA_URL [http://homeassistant.local:8123]: ');
    if (url || process.env.HA_URL) {
      const token = await ask('HA_TOKEN (long-lived access token, Enter = saltar): ');
      await writeEnv(base, 'homeassistant-mcp', [
        `HA_URL=${url || process.env.HA_URL || 'http://homeassistant.local:8123'}`,
        `HA_TOKEN=${token || process.env.HA_TOKEN || ''}`,
      ]);
    }
  }

  // Gmail — just point to where user should put credentials
  if (fileExists(path.join(base, 'gmail-mcp'))) {
    console.log('\nGmail: coloca credentials.json y token.json en:', path.join(base, 'gmail-mcp'));
    console.log('Ejecuta: python gmail_auth.py para autenticar');
  }
}

async function installCommand(args) {
  const sourcePath = args.includes('--source') ? args[args.indexOf('--source') + 1] : null;
  const selectedAgents = args.filter(a => !a.startsWith('--') && a !== sourcePath);

  const repoDir = ensureRepo(sourcePath);
  console.log(`\nUsando repo en: ${repoDir}\n`);

  const { detectAgents, AGENTS } = require('./agents');
  let agents = selectedAgents.length > 0
    ? AGENTS.filter(a => selectedAgents.includes(a.id))
    : detectAgents();

  if (agents.length === 0) {
    console.log('No se detectaron agentes de IA instalados.');
    console.log('Instala uno de: OpenCode, Claude Desktop, Claude Code, Cursor, Kiro, Windsurf, OpenClaw');
    console.log('O especifica agentes: mcps-ai install opencode claude');
    return;
  }

  console.log('Agentes detectados:');
  agents.forEach(a => console.log(`  - ${a.name} (${a.id})`));
  console.log('');

  // Install dependencies once (shared repo copy)
  console.log('Instalando dependencias Python...');
  for (const agent of agents) {
    installMcpDependencies(repoDir, agent.id);
  }

  // Prompt for credentials once
  await promptCredentials(repoDir, agents[0].id);

  // Write configs for each agent
  for (const agent of agents) {
    console.log(`\nConfigurando ${agent.name}...`);
    const mcpConfig = getMcpConfigs(agent.id, repoDir);
    agent.writeConfig(mcpConfig);
    console.log(`  ✓ ${agent.name} configurado en ${agent.configPath()}`);
  }

  console.log('\n✅ Instalación completa!');
  console.log('Reinicia tu agente de IA para cargar los MCPs.');
}

async function updateCommand() {
  const repoDir = ensureRepo();
  const { detectAgents, AGENTS } = require('./agents');
  const agents = detectAgents();

  console.log('Actualizando instalación (conservando .env y credenciales)...');
  for (const agent of agents) {
    installMcpDependencies(repoDir, agent.id);
  }
  // Re-apply configs (idempotent)
  for (const agent of agents) {
    const mcpConfig = getMcpConfigs(agent.id, repoDir);
    agent.writeConfig(mcpConfig);
    console.log(`  ✓ ${agent.name} actualizado`);
  }
  console.log('\n✅ Actualización completa. Tus credenciales y .env se conservaron.');
}

function statusCommand() {
  const { detectAgents } = require('./agents');
  const agents = detectAgents();
  console.log('Agentes detectados:');
  if (agents.length === 0) {
    console.log('  (ninguno)');
    return;
  }
  agents.forEach(a => {
    console.log(`  ✓ ${a.name}`);
    console.log(`    Config: ${a.configPath()}`);
  });
  if (dirExists(REPO_DIR)) {
    console.log(`\nRepo instalado en: ${REPO_DIR}`);
    try {
      const version = execSync('git log --oneline -1', { cwd: REPO_DIR }).toString().trim();
      console.log(`Versión: ${version}`);
    } catch {}
  } else {
    console.log('\nRepo no clonado todavía. Ejecuta: mcps-ai install');
  }
}

function doctorCommand() {
  const { detectAgents } = require('./agents');
  const agents = detectAgents();
  console.log('Diagnóstico:\n');
  agents.forEach(a => {
    const configPath = a.configPath();
    const hasConfig = fileExists(configPath);
    console.log(`  ${hasConfig ? '✓' : '✗'} ${a.name}: ${hasConfig ? 'configurado' : 'no configurado'} (${configPath})`);
  });
  console.log('');
  // Check uv
  const uvPath = path.join(os.homedir(), '.local/bin/uv');
  console.log(`  ${fileExists(uvPath) ? '✓' : '✗'} uv: ${fileExists(uvPath) ? uvPath : 'no encontrado'}`);
  // Check repo
  console.log(`  ${dirExists(REPO_DIR) ? '✓' : '✗'} repo: ${dirExists(REPO_DIR) ? REPO_DIR : 'no clonado'}`);
}

module.exports = { installCommand, updateCommand, statusCommand, doctorCommand, INSTALL_DIR, REPO_DIR };
