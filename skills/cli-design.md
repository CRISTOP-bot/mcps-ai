---
name: cli-design
description: Diseño de CLIs con Node/Python buenas prácticas. Se activa cuando se trabaja en mcps-ai o el worker.
---

# Skill: Diseño de CLI

## Buenas prácticas
1. `--help` y `-h` para todos los comandos
2. Flags con `--` (ej: `--source`)
3. Exit codes: 0 = ok, 1 = error del usuario, 2 = error interno
4. Colores útiles (no más del necesario)
5. `--dry-run` para previsualizar

## Node.js
```javascript
const cli = require('commander');
cli.command('install').action((opts) => { ... });
cli.parse();
```

## Python (Click / Typer)
```python
@app.command()
def install(source: str = typer.Option(None)):
    ...
typer.run(install)
```

## Node vs Python
- Node: distribución npm, npx, install rápido
- Python: mcps-ai worker usa FastMCP, más cómodo para AI
