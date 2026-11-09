---
name: gpg-signing
description: Firmar commits y tags con GPG/SSH. Se activa cuando se configura firma en git.
---

# Skill: Firma GPG

## Con SSH (más simple, moderno)
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

## Verificar
```bash
git log --show-signature
```
