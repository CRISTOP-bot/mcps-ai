---
name: rcon-cheatsheet
description: Comandos útiles de Minecraft RCON para administración de servidor. Se activa cuando el admin pide ayuda con su server MC.
---

# Skill: Minecraft RCON cheatsheet

## Admin
```
/list                # jugadores online
/whitelist add <p>   # añadir a whitelist
/whitelist remove <p>
/op <p>              # dar admin
/deop <p>
/kick <p> [razón]
/ban <p> [razón]
/pardon <p>
```

## World
```
/time set day|night|noon|midnight
/weather clear|rain|thunder
/difficulty peaceful|easy|normal|hard
/gamemode survival|creative|adventure|spectator <p>
/tp <p> <x> <y> <z>
```

## Items
```
/give <p> <item> [cantidad]
/give <p> minecraft:diamond_block 64
```

## Mobs
```
/summon <mob> [x y z]
/kill <selector>   # @e = todos, @a = jugadores
```

## Efectos
```
/effect give <p> speed 60 2
```
