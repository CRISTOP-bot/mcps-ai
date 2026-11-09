---
name: ssh-key-management
description: Gestionar llaves SSH — generar, ssh-agent, config, rotación. Se activa cuando se trabaja con SSH/git remoto.
---

# Skill: SSH keys

## Generar
```bash
ssh-keygen -t ed25519 -C "email@example.com"
ssh-copy-id usuario@host
```

## ssh-agent
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

## ~/.ssh/config
```
Host github.com
  IdentityFile ~/.ssh/id_ed25519
  User git
```
