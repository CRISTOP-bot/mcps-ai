---
name: terraform-basics
description: Terraform básico para IaC — init, plan, apply, estado. Se activa cuando se usa infraestructura como código.
---

# Skill: Terraform

## Flujo
```bash
terraform init
terraform plan    # revisar diff antes de aplicar
terraform apply   # con aprobación
```

## Reglas
- Estado remoto (no terraform.tfstate en git)
- plan siempre antes de apply
- Módulos para reuso
