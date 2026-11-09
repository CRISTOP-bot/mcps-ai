const { installCommand, updateCommand, statusCommand, doctorCommand } = require('./install');

const HELP = `
mcps-ai - Instalador y actualizador universal de MCPs

Uso:
  mcps-ai install [agentes...]   Instala y configura los MCPs para tus agentes de IA
  mcps-ai update                 Actualiza los MCPs sin perder tus credenciales
  mcps-ai status                 Muestra qué agentes están detectados y configurados
  mcps-ai doctor                 Diagnóstico de la instalación
  mcps-ai help                   Esta ayuda

Ejemplos:
  mcps-ai install                Detecta e instala todo automáticamente
  mcps-ai install opencode       Instala solo para OpenCode
  mcps-ai update                 Actualiza sin perder .env

Opciones:
  --source <path>                Usar un directorio local como fuente (en vez de clonar de GitHub)

Notas:
  - Detecta automáticamente: OpenCode, Claude Desktop, Claude Code, Cursor, Kiro, Windsurf, OpenClaw
  - Tus credenciales (.env, credentials.json) NUNCA se sobrescriben en updates
  - Para usar credenciales propias: edita .env después de instalar
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
