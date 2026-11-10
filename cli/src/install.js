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

function commandExistsSimple(cmd) {
  try { execSync(`which ${cmd} 2>/dev/null`, { stdio: 'pipe' }); return true; } catch { return false; }
}

function resolveUv() {
  const candidates = [path.join(os.homedir(), '.local/bin/uv'), 'uv'];
  for (const c of candidates) {
    if (c.startsWith('/') ? fileExists(c) : commandExistsSimple(c)) return c;
  }
  return null;
}

function tcpProbe(host, port, ms = 800) {
  return new Promise(resolve => {
    try {
      const net = require('net');
      const s = new net.Socket();
      s.setTimeout(ms);
      s.once('connect', () => { s.destroy(); resolve(true); });
      s.once('timeout', () => { s.destroy(); resolve(false); });
      s.once('error', () => { s.destroy(); resolve(false); });
      s.connect(port, host);
    } catch { resolve(false); }
  });
}

function httpProbe(url, ms = 1500) {
  return new Promise(resolve => {
    try {
      const req = https.get(url, { timeout: ms }, res => {
        res.resume();
        resolve(res.statusCode < 500);
      });
      req.on('timeout', () => { req.destroy(); resolve(false); });
      req.on('error', () => resolve(false));
    } catch { resolve(false); }
  });
}

function tryGhToken() {
  try {
    execSync('which gh', { stdio: 'pipe' });
    const token = execSync('gh auth token', { stdio: 'pipe', encoding: 'utf8', timeout: 5000 }).trim();
    return token || null;
  } catch { return null; }
}

// Best-effort auto-configuration of connectors that are trivial to set up.
// NEVER overwrites an existing .env; NEVER prints secrets.
async function autoConfigure(repoDir, { interactive = false } = {}) {
  const base = path.join(repoDir, 'mcps');
  const done = [];

  // 1) GitHub — token from gh CLI (zero config)
  const ghEnv = path.join(base, 'github-mcp', '.env');
  if (dirExists(path.join(base, 'github-mcp')) && !fileExists(ghEnv)) {
    const token = tryGhToken();
    if (token) {
      fs.writeFileSync(ghEnv, `GITHUB_TOKEN=${token}
`, { mode: 0o600 });
      done.push('github (token desde gh CLI, chmod 600)');
    } else {
      done.push('github (gh CLI sin auth; sin configurar)');
    }
  } else if (fileExists(ghEnv)) {
    done.push('github (.env existente, preservado)');
  }

  // 2) Browser — Playwright chromium (zero config)
  const pwCache = path.join(os.homedir(), '.cache', 'ms-playwright');
  if (dirExists(path.join(base, 'browser-mcp'))) {
    if (dirExists(pwCache)) {
      done.push('browser (chromium ya instalado)');
    } else {
      try {
        console.log('  Instalando Playwright chromium (puede tardar 1-2 min)...');
        run('uv run playwright install chromium', path.join(base, 'browser-mcp'));
        done.push('browser (chromium instalado)');
      } catch {
        done.push('browser (playwright install falló; ejecuta: cd mcps/browser-mcp && uv run playwright install chromium)');
      }
    }
  }

  // 3) Orchestrator — reuse AI_* from the telegram worker config (zero config)
  const orchEnv = path.join(base, 'orchestrator-mcp', '.env');
  if (dirExists(path.join(base, 'orchestrator-mcp')) && !fileExists(orchEnv)) {
    const candidates = [
      path.join(base, 'telegram-mcp', '.env'),
      path.join(os.homedir(), 'mcp-servers', 'telegram-mcp', '.env'),
    ];
    let configured = false;
    for (const src of candidates) {
      if (fileExists(src)) {
        const keep = fs.readFileSync(src, 'utf8').split('\n')
          .filter(l => /^(AI_BASE_URL|AI_PASSWORD|AI_AUTH_USER|AI_DIRECTORY|AI_MODEL_ID|AI_MODEL_PROVIDER)=/.test(l.trim()));
        if (keep.length) {
          fs.writeFileSync(orchEnv,
            [...keep, 'REQUEST_TIMEOUT=0', 'DATABASE_PATH=./data/orchestra.db'].join('\n') + '\n',
            { mode: 0o600 });
          done.push(`orchestrator (AI_* reutilizado de ${src.includes('mcp-servers') ? '~/mcp-servers/telegram-mcp/.env' : 'telegram-mcp del repo'})`);
          configured = true;
          break;
        }
      }
    }
    if (!configured) {
      // Auto-detect the OpenCode Server port, then leave the rest for the prompt
      const up49374 = await tcpProbe('127.0.0.1', 49374);
      const port = up49374 ? '49374' : ((await tcpProbe('127.0.0.1', 4096)) ? '4096' : '4096');
      fs.writeFileSync(orchEnv,
        `AI_BASE_URL=http://127.0.0.1:${port}\nAI_PASSWORD=\nAI_AUTH_USER=opencode\nAI_DIRECTORY=${os.homedir()}\nAI_MODEL_ID=deepseek-v4.1-flash-free\nAI_MODEL_PROVIDER=opencode\nREQUEST_TIMEOUT=0\nDATABASE_PATH=./data/orchestra.db\n`,
        { mode: 0o600 });
      done.push(`orchestrator (AI_BASE_URL detectado en :${port}; falta AI_PASSWORD)`);
    }
  } else if (fileExists(orchEnv)) {
    done.push('orchestrator (.env existente, preservado)');
  }

  // 4) Home Assistant — detect reachable instance (URL only; token is personal)
  const haEnv = path.join(base, 'homeassistant-mcp', '.env');
  if (dirExists(path.join(base, 'homeassistant-mcp')) && !fileExists(haEnv)) {
    const candidates = ['http://homeassistant.local:8123', 'http://127.0.0.1:8123'];
    let detected = '';
    for (const u of candidates) {
      if (await httpProbe(u + '/api/')) { detected = u; break; }
    }
    if (detected) {
      fs.writeFileSync(haEnv, `HA_URL=${detected}\nHA_TOKEN=\n`, { mode: 0o600 });
      done.push(`homeassistant (instancia detectada en ${detected}; falta HA_TOKEN)`);
    } else {
      done.push('homeassistant (no se detectó instancia; configura HA_URL/HA_TOKEN manualmente)');
    }
  } else if (fileExists(haEnv)) {
    done.push('homeassistant (.env existente, preservado)');
  }

  // 5) Minecraft — detect local server, still needs RCON password (prompted later)
  if (dirExists(path.join(base, 'minecraft-mcp'))) {
    const mcUp = await tcpProbe('127.0.0.1', 25575);
    done.push(mcUp ? 'minecraft (server local detectado en :25575)' : 'minecraft (sin server local; se pedirá MC_HOST en el prompt)');
  }

  if (done.length) {
    console.log('\nAuto-configuración:');
    for (const d of done) console.log(`  ✓ ${d}`);
  }
  return done;
}

function backupConfig(p) {
  if (fileExists(p)) {
    const backup = p + '.bak.' + Date.now();
    fs.copyFileSync(p, backup);
    try { fs.chmodSync(backup, 0o600); } catch {}
    return backup;
  }
  return null;
}

// Best-effort sweep: every MCP .env in the repo gets owner-only permissions.
function secureEnvFiles(repoDir) {
  try {
    const base = path.join(repoDir, 'mcps');
    if (!dirExists(base)) return;
    for (const d of fs.readdirSync(base, { withFileTypes: true })) {
      if (!d.isDirectory()) continue;
      const env = path.join(base, d.name, '.env');
      if (fileExists(env)) {
        try { fs.chmodSync(env, 0o600); } catch {}
      }
    }
  } catch {}
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
  try {
    run(`git clone --depth 1 ${REPO_URL} ${REPO_DIR}`);
  } catch (e) {
    console.error(`ERROR: no se pudo clonar ${REPO_URL}`);
    console.error('Revisa tu conexión o apunta a un clon local: mcps-ai install --source /ruta/a/mcps-ai');
    process.exit(1);
  }
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
  if (fileExists(path.join(base, 'orchestrator-mcp', 'main.py'))) {
    const env = {};
    if (process.env.AI_PASSWORD) env.AI_PASSWORD = process.env.AI_PASSWORD;
    if (process.env.AI_BASE_URL) env.AI_BASE_URL = process.env.AI_BASE_URL;
    config.orchestrator = {
      type: 'local',
      command: [path.join(os.homedir(), '.local/bin/uv'), '--directory', path.join(base, 'orchestrator-mcp'), 'run', 'main.py'],
      env,
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
  if (dirExists(path.join(base, 'telegram-mcp'))) {
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
  if (dirExists(path.join(base, 'minecraft-mcp'))) {
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
  if (dirExists(path.join(base, 'github-mcp'))) {
    const token = await ask('GITHUB_TOKEN (Enter = intentar `gh auth token` en tiempo de ejecución, o saltar): ');
    if (token) {
      await writeEnv(base, 'github-mcp', [`GITHUB_TOKEN=${token}`]);
    }
  }

  // Discord
  if (dirExists(path.join(base, 'discord-mcp'))) {
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
  if (dirExists(path.join(base, 'spotify-mcp'))) {
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
  if (dirExists(path.join(base, 'slack-mcp'))) {
    const token = await ask('SLACK_BOT_TOKEN (xoxb-..., Enter = saltar): ');
    if (token) {
      await writeEnv(base, 'slack-mcp', [`SLACK_BOT_TOKEN=${token}`]);
    }
  }

  // Notion
  if (dirExists(path.join(base, 'notion-mcp'))) {
    const key = await ask('NOTION_API_KEY (ntn_/secret_..., Enter = saltar): ');
    if (key) {
      await writeEnv(base, 'notion-mcp', [`NOTION_API_KEY=${key}`]);
    }
  }

  // Home Assistant
  if (dirExists(path.join(base, 'homeassistant-mcp'))) {
    const url = await ask('HA_URL [http://homeassistant.local:8123]: ');
    if (url || process.env.HA_URL) {
      const token = await ask('HA_TOKEN (long-lived access token, Enter = saltar): ');
      await writeEnv(base, 'homeassistant-mcp', [
        `HA_URL=${url || process.env.HA_URL || 'http://homeassistant.local:8123'}`,
        `HA_TOKEN=${token || process.env.HA_TOKEN || ''}`,
      ]);
    }
  }

  // Orchestrator (OpenCode Server)
  if (dirExists(path.join(base, 'orchestrator-mcp'))) {
    const url = await ask('AI_BASE_URL [http://127.0.0.1:4096]: ');
    const pass = await ask('AI_PASSWORD (OpenCode Server password, Enter = saltar): ');
    const lines = [];
    if (url) lines.push(`AI_BASE_URL=${url}`);
    if (pass) lines.push(`AI_PASSWORD=${pass}`);
    if (lines.length) {
      lines.push('AI_AUTH_USER=' + (process.env.AI_AUTH_USER || 'opencode'));
      lines.push('AI_DIRECTORY=' + os.homedir());
      lines.push('AI_MODEL_ID=' + (process.env.AI_MODEL_ID || 'deepseek-v4.1-flash-free'));
      lines.push('AI_MODEL_PROVIDER=' + (process.env.AI_MODEL_PROVIDER || 'opencode'));
      lines.push('REQUEST_TIMEOUT=0');
      lines.push('DATABASE_PATH=./data/orchestra.db');
      await writeEnv(base, 'orchestrator-mcp', lines);
    }
  }

  // Gmail — just point to where user should put credentials
  if (dirExists(path.join(base, 'gmail-mcp'))) {
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

  // Preflight checks — fail fast with a clear message
  if (!commandExistsSimple('git')) {
    console.error('ERROR: git no está instalado. Instálalo primero: https://git-scm.com/');
    process.exit(1);
  }
  if (!resolveUv()) {
    console.error('ERROR: uv no encontrado (ni en ~/.local/bin/uv ni en PATH).');
    console.error('Instálalo con: curl -LsSf https://astral.sh/uv/install.sh | sh');
    process.exit(1);
  }

  // Install dependencies once (shared repo copy)
  console.log('Instalando dependencias Python...');
  for (const agent of agents) {
    installMcpDependencies(repoDir, agent.id);
  }

  // Auto-configure connectors that are trivial to set up
  await autoConfigure(repoDir, { interactive: true });

  // Prompt for credentials once
  await promptCredentials(repoDir, agents[0].id);

  // Write configs for each agent
  for (const agent of agents) {
    console.log(`\nConfigurando ${agent.name}...`);
    const mcpConfig = getMcpConfigs(agent.id, repoDir);
    agent.writeConfig(mcpConfig);
    console.log(`  ✓ ${agent.name} configurado en ${agent.configPath()}`);
  }

  secureEnvFiles(repoDir);

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
  await autoConfigure(repoDir, { interactive: false });
  // Re-apply configs (idempotent)
  for (const agent of agents) {
    const mcpConfig = getMcpConfigs(agent.id, repoDir);
    agent.writeConfig(mcpConfig);
    console.log(`  ✓ ${agent.name} actualizado`);
  }
  secureEnvFiles(repoDir);
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

module.exports = { installCommand, updateCommand, statusCommand, doctorCommand, INSTALL_DIR, REPO_DIR, _test: { dirExists, fileExists } };
