const { installCommand, updateCommand, statusCommand, doctorCommand } = require('./install');
const { loginCommand, logoutCommand, backupCommand, restoreCommand } = require('./github');

const HELP = `
mcps-ai - Instalador y actualizador universal de MCPs

Uso:
  mcps-ai install [agentes...]   Instala y configura los MCPs para tus agentes de IA
  mcps-ai update                 Actualiza los MCPs sin perder tus credenciales
  mcps-ai status                 Muestra qué agentes están detectados y configurados
  mcps-ai doctor                 Diagnóstico de la instalación
  mcps-ai login                  Inicia sesión con GitHub (device flow)
  mcps-ai logout                 Cierra sesión de GitHub
  mcps-ai backup                 Respalda tus credenciales en un Gist privado
  mcps-ai restore                Restaura credenciales desde el Gist
  mcps-ai help                   Esta ayuda

Ejemplos:
  mcps-ai install                Detecta e instala todo automáticamente
  mcps-ai install opencode       Instala solo para OpenCode
  mcps-ai update                 Actualiza sin perder .env
  mcps-ai login                  Autentica con GitHub
  mcps-ai backup                 Sube tus credenciales a tu cuenta
  mcps-ai restore                Recupera credenciales en otra máquina

Notas:
  - Los backups son Gists privados en tu cuenta de GitHub
  - Tus .env y token.json nunca se suben a GitHub público
  - Detecta automáticamente: OpenCode, Claude Desktop, Claude Code, Cursor, Kiro, Windsurf, OpenClaw
`;

async function main(args) {
  const cmd = args[0] || 'help';

  switch (cmd) {
    case 'install':
      await installCommand(args.slice(1));
      break;
    case 'update':
      await updateCommand();
      break;
    case 'status':
      statusCommand();
      break;
    case 'doctor':
      doctorCommand();
      break;
    case 'login':
      await loginCommand();
      break;
    case 'logout':
      logoutCommand();
      break;
    case 'backup':
      await backupCommand();
      break;
    case 'restore':
      await restoreCommand();
      break;
    case 'help':
    case '--help':
    case '-h':
      console.log(HELP);
      break;
    default:
      console.log(`Comando desconocido: ${cmd}`);
      console.log(HELP);
      process.exit(1);
  }
}

module.exports = { main };
