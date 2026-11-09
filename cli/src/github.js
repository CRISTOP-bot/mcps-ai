// GitHub Device Flow OAuth + credential backup via private Gist
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const { execSync } = require('child_process');
const readline = require('readline');

const CRED_DIR = path.join(os.homedir(), '.mcps-ai');
const CRED_FILE = path.join(CRED_DIR, 'github-token');
const GIST_DESCRIPTION = 'mcps-ai credentials backup (private)';

function httpsRequest(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, headers: res.headers, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, headers: res.headers, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

function saveToken(token) {
  fs.mkdirSync(CRED_DIR, { recursive: true });
  fs.writeFileSync(CRED_FILE, token, { mode: 0o600 });
}

function getToken() {
  if (fs.existsSync(CRED_FILE)) {
    return fs.readFileSync(CRED_FILE, 'utf8').trim();
  }
  return null;
}

function promptUserCode(userCode, verificationUrl) {
  console.log('\n  Abre esta URL en tu navegador:');
  console.log(`  ${verificationUrl}\n`);
  console.log(`  E ingresa este código: ${userCode}\n`);
  console.log('  Esperando autenticación...');
}

async function loginCommand() {
  const clientId = process.env.MCPS_AI_GITHUB_CLIENT_ID || 'Iv23liXy4Dz7g8hDTlzK'; // public client id
  // Request device code
  const res = await httpsRequest({
    hostname: 'github.com',
    path: '/login/device/code',
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'User-Agent': 'mcps-ai-cli',
    },
  }, JSON.stringify({ client_id: clientId, scope: 'gist read:user' }));

  if (res.status !== 200 || !res.body.device_code) {
    console.error('Error obteniendo device code:', res.body);
    process.exit(1);
  }

  const { device_code, user_code, verification_uri, interval } = res.body;
  promptUserCode(user_code, verification_uri);

  // Poll for token
  const pollInterval = (interval || 5) * 1000;
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, pollInterval));
    const poll = await httpsRequest({
      hostname: 'github.com',
      path: '/login/oauth/access_token',
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'mcps-ai-cli',
      },
    }, JSON.stringify({ client_id: clientId, device_code, grant_type: 'urn:ietf:params:oauth:grant-type:device_code' }));

    if (poll.body.access_token) {
      saveToken(poll.body.access_token);
      console.log('\n  ✓ Autenticado con GitHub');
      const user = await apiGet('/user', poll.body.access_token);
      console.log(`  Usuario: ${user.login}`);
      return;
    }
    if (poll.body.error === 'slow_down') {
      await new Promise(r => setTimeout(r, 5000));
    }
    if (poll.body.error === 'authorization_pending') continue;
    if (poll.body.error === 'expired_token') {
      console.error('\n  Token expirado. Intenta de nuevo.');
      process.exit(1);
    }
    if (poll.body.error === 'access_denied') {
      console.error('\n  Acceso denegado.');
      process.exit(1);
    }
  }
  console.error('\n  Timeout esperando autenticación.');
  process.exit(1);
}

async function apiGet(path, token) {
  const res = await httpsRequest({
    hostname: 'api.github.com',
    path,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'User-Agent': 'mcps-ai-cli',
      'X-GitHub-Api-Version': '2022-11-28',
    },
  });
  return res.body;
}

async function apiPost(path, body, token) {
  const data = JSON.stringify(body);
  const res = await httpsRequest({
    hostname: 'api.github.com',
    path,
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'User-Agent': 'mcps-ai-cli',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(data),
    },
  }, data);
  return res;
}

async function findBackupGist(token) {
  const gists = await apiGet('/gists?per_page=100', token);
  if (Array.isArray(gists)) {
    return gists.find(g => g.description === GIST_DESCRIPTION) || null;
  }
  return null;
}

function collectCredentialFiles() {
  const files = {};
  const home = os.homedir();
  // .env files from installed MCPs
  const dirs = [
    path.join(home, 'mcp-servers/telegram-mcp'),
    path.join(home, 'mcp-servers/minecraft-mcp'),
    path.join(home, 'mcp-servers/gmail-mcp'),
    path.join(home, '.mcps-ai/repo/agents'), // if installed via CLI
  ];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      const p = path.join(dir, name);
      if (fs.statSync(p).isFile() && (name === '.env' || name === 'credentials.json' || name === 'token.json')) {
        files[`.mcps-ai/${name}`] = fs.readFileSync(p, 'utf8');
      }
    }
  }
  // Also shared opencode config (backup only, not a secret)
  const opencode = path.join(home, '.config/opencode/opencode.json');
  if (fs.existsSync(opencode)) files['.config/opencode/opencode.json'] = fs.readFileSync(opencode, 'utf8');
  const kiro = path.join(home, '.kiro/settings/mcp.json');
  if (fs.existsSync(kiro)) files['.kiro/settings/mcp.json'] = fs.readFileSync(kiro, 'utf8');
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
    const safeName = name.replace(/[^a-zA-Z0-9._-]/g, '_');
    fileEntries[safeName] = { content };
  }

  const payload = {
    description: GIST_DESCRIPTION,
    public: false,
    files: fileEntries,
  };

  const existing = await findBackupGist(token);
  if (existing) {
    const res = await httpsRequest({
      hostname: 'api.github.com',
      path: `/gists/${existing.id}`,
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'mcps-ai-cli',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
    }, JSON.stringify(payload));
    console.log('✓ Backup actualizado:', `https://gist.github.com/${token ? '' : ''}${existing.id}`);
  } else {
    const res = await apiPost('/gists', payload, token);
    if (res.status === 201) {
      console.log('✓ Backup creado (gist privado):', res.body.html_url);
    } else {
      console.error('Error creando gist:', res.body);
      process.exit(1);
    }
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
    console.error('No se encontró backup en tu GitHub. Ejecuta: mcps-ai backup primero');
    process.exit(1);
  }

  const gist = await apiGet(`/gists/${existing.id}`, token);
  console.log('Archivos a restaurar:');
  for (const [name] of Object.entries(gist.files)) {
    console.log(`  - ${name}`);
  }

  const answer = await ask('¿Restaurar? Esto sobrescribirá archivos locales existentes. [y/N]: ');
  if (answer.toLowerCase() !== 'y') {
    console.log('Cancelado.');
    return;
  }

  for (const [name, file] of Object.entries(gist.files)) {
    const dest = name.startsWith('.mcps-ai/')
      ? path.join(os.homedir(), name.replace(/^\.mcps-ai\//, '.mcps-ai/'))
      : path.join(os.homedir(), name);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    // Backup existing
    if (fs.existsSync(dest)) fs.copyFileSync(dest, dest + '.bak');
    fs.writeFileSync(dest, file.content);
    console.log(`  ✓ Restaurado: ${dest}`);
  }
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, answer => { rl.close(); resolve(answer.trim()); }));
}

function logoutCommand() {
  if (fs.existsSync(CRED_FILE)) {
    fs.unlinkSync(CRED_FILE);
    console.log('✓ Sesión de GitHub cerrada');
  } else {
    console.log('No estabas autenticado');
  }
}

module.exports = { loginCommand, logoutCommand, backupCommand, restoreCommand };
