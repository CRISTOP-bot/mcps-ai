---
name: advanced-debugging
description: Técnicas avanzadas de debugging — bisect, core dumps, profilers. Se activa cuando el bug es esquivo.
---

# Skill: Debugging avanzado

## git bisect
```bash
git bisect start
git bisect bad HEAD
git bisect good <sha-bueno>
# probará commits; marca good/bad
```

## Python
- `python -X dev script.py` — warnings extra
- `faulthandler.enable()` — traceback en C crashes
- `py-spy dump --pid <pid>` — stack de proceso vivo

## Node
- `node --inspect` + Chrome DevTools
- `clinic doctor -- node app.js`
