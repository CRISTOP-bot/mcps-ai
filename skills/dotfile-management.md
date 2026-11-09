---
name: dotfile-management
description: Gestionar dotfiles — git, symlinks, stow. Se activa cuando el usuario quiere versionar su config.
---

# Skill: Dotfiles

## Enfoque
```bash
git init ~/.dotfiles
mv ~/.bashrc ~/.dotfiles/
ln -s ~/.dotfiles/.bashrc ~/.bashrc
```

## O con stow
```bash
stow .
```

## Regla de oro
NUNCA commitear credenciales; .env aparte con .gitignore
