// GitHub auth via gh CLI + credential backup via private Gist
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, execFileSync } = require('child_process');
const readline = require('readline');

const CRED_DIR = path.join(os.homedir(), '.mcps-ai');
const CRED_FILE = path.join(CRED_DIR, 'github-token');
const GIST_DESCRIPTION = 'mcps-ai credentials backup (private)';

function getToken() {
  if (fs.existsSync(CRED_FILE)) {
    return fs.readFileSync(CRED_FILE, 'utf8').trim();
  }
  // Try gh CLI (already logged in)
  try {
    const token = execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim();
    if (token) {
      saveToken(token);
      return token;
    }
  } catch {}
  return null;
}

function saveToken(token) {
  fs.mkdirSync(CRED_DIR, { recursive: true });
  fs.writeFileSync(CRED_FILE, token, { mode: 0o600 });
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, answer => { rl.close(); resolve(answer.trim()); }));
}

async function loginCommand() {
  console.log('Autenticando con GitHub...\n');

  // Try gh CLI first
  try {
    const token = execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim();
    if (token) {
      saveToken(token);
      const user = execFileSync('gh', ['api', 'user', '--jq', '.login'], { encoding: 'utf8' }).trim();
      console.log(`  ✓ Autenticado como: ${user}`);
      console.log('  Token guardado en ~/.mcps-ai/github-token');
      return;
    }
  } catch {}

  // gh not installed/logged in — guide user
  console.log('gh CLI no encontrado o no autenticado.');
  console.log('');
  console.log('Opción 1 (recomendada): Instala gh y haz login:');
  console.log('  sudo apt install gh');
  console.log('  gh auth login');
  console.log('  mcps-ai login   # Ahora funciona automáticamente');
  console.log('');
  console.log('Opción 2: Crea un Personal Access Token en GitHub');
  console.log('  https://github.com/settings/tokens');
  console.log('  Scopes: gist, read:user, repo');
  console.log('');
  const token = await ask('Pega tu token aquí (o Enter para cancelar): ');
  if (token) {
    saveToken(token);
    console.log('  ✓ Token guardado');
  } else {
    console.log('Cancelado.');
  }
}

function logoutCommand() {
  if (fs.existsSync(CRED_FILE)) {
    fs.unlinkSync(CRED_FILE);
    console.log('✓ Sesión cerrada (token eliminado)');
    console.log('Nota: gh auth logout también funciona si quieres cerrar gh.');
  } else {
    console.log('No estabas autenticado');
  }
}

async function apiGet(path, token) {
  const res = execFileSync('gh', ['api', path, '--jq', '.'], { encoding: 'utf8', input: '' });
  return JSON.parse(res);
}

async function apiRequest(method, path, body, token) {
  const args = ['api', '--method', method, path, '--jq', '.'];
  if (body) {
    args.push('--input', '-');
    const res = execFileSync('gh', args, {
      encoding: 'utf8',
      input: JSON.stringify(body),
    });
    return JSON.parse(res);
  }
  const res = execFileSync('gh', args, { encoding: 'utf8' });
  return res;
}

async function findBackupGist(token) {
  try {
    const gists = await apiGet('/gists?per_page=100', token);
    return gists.find(g => g.description === GIST_DESCRIPTION) || null;
  } catch {
    return null;
  }
}

function collectCredentialFiles() {
  const files = {};
  const home = os.homedir();
  const dirs = [
    path.join(home, 'mcp-servers', 'telegram-mcp'),
    path.join(home, 'mcp-servers', 'minecraft-mcp'),
    path.join(home, 'mcp-servers', 'gmail-mcp'),
    path.join(home, '.mcps-ai', 'repo', 'agents'),
  ];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    const names = fs.readdirSync(dir, { withFileTypes: true })
      .filter(e => e.isFile() && ['.env', 'credentials.json', 'token.json'].includes(e.name));
    for (const e of names) {
      const rel = path.relative(home, path.join(dir, e.name));
      files[`backup/${e.name}`] = fs.readFileSync(path.join(dir, e.name), 'utf8');
    }
  }
  // Also agent configs
  const agentConfigs = [
    ['opencode.json', path.join(home, '.config', 'opencode', 'opencode.json')],
    ['kiro-mcp.json', path.join(home, '.kiro', 'settings', 'mcp.json')],
    ['claude_desktop_config.json', path.join(home, '.config', 'claude', 'claude_desktop_config.json')],
  ];
  for (const [name, p] of agentConfigs) {
    if (fs.existsSync(p)) files[`backup/${name}`] = fs.readFileSync(p, 'utf8');
  }
  return files;
}

async function backupCommand() {
  const token = getToken();
  if (!token) {
    console.error('No autenticado. Ejecuta: mcps-ai login');
    process.exit(1);
  }

  const files = collectCredentialFiles();
  const fileEntries = {};
  for (const [name, content] of Object.entries(files)) {
    fileEntries[name.replace(/[^a-zA-Z0-9._-]/g, '_')] = { content };
  }

  const payload = { description: GIST_DESCRIPTION, public: false, files: fileEntries };

  const existing = await findBackupGist(token);
  if (existing) {
    await apiRequest('PATCH', `/gists/${existing.id}`, payload, token);
    console.log('✓ Backup actualizado (Gist privado):', `https://gist.github.com/${existing.id}`);
  } else {
    const res = await apiRequest('POST', '/gists', payload, token);
    console.log('✓ Backup creado (Gist privado):', res.html_url);
  }
}

async function restoreCommand() {
  const token = getToken();
  if (!token) {
    console.error('No autenticado. Ejecuta: mcps-ai login');
    process.exit(1);
  }

  const existing = await findBackupGist(token);
  if (!existing) {
    console.error('No se encontró backup. Ejecuta: mcps-ai backup primero');
    process.exit(1);
  }

  const gist = await apiGet(`/gists/${existing.id}`, token);
  console.log('Archivos en el backup:');
  for (const name of Object.keys(gist.files)) {
    console.log(`  - ${name}`);
  }

  const answer = await ask('¿Restaurar? Sobrescribe archivos locales. [y/N]: ');
  if (answer.toLowerCase() !== 'y') {
    console.log('Cancelado.');
    return;
  }

  const home = os.homedir();
  for (const [name, file] of Object.entries(gist.files)) {
    const clean = name.replace(/^backup_/, '');
    let dest;
    if (clean === 'opencode.json') dest = path.join(home, '.config', 'opencode', 'opencode.json');
    else if (clean === 'kiro-mcp.json') dest = path.join(home, '.kiro', 'settings', 'mcp.json');
    else if (clean === 'claude_desktop_config.json') dest = path.join(home, '.config', 'claude', 'claude_desktop_config.json');
    else if (clean.endsWith('.env') || clean === 'credentials.json' || clean === 'token.json') {
      // Find which MCP it belongs to by current contents
      dest = path.join(home, '.mcps-ai', 'restored', clean);
    } else {
      dest = path.join(home, '.mcps-ai', 'restored', clean);
    }
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    if (fs.existsSync(dest)) fs.copyFileSync(dest, dest + '.bak');
    fs.writeFileSync(dest, file.content);
    console.log(`  ✓ Restaurado: ${dest}`);
  }
  console.log('\nNota: los .env se restauran en ~/.mcps-ai/restored/ — cópialos a tus MCP dirs.');
}

module.exports = { loginCommand, logoutCommand, backupCommand, restoreCommand };
