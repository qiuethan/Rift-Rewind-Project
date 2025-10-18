# Riot Timeline Schemas

Source: `riot_outputs/timeline_NA1_5377521793.json`

## Frames

### Frame
```json
{
  "events": [Event],
  "participantFrames": { "1": ParticipantFrame, "2": ParticipantFrame, ..., "10": ParticipantFrame }
}
```

### ParticipantFrame
```json
{
  "championStats": ChampionStats,
  "currentGold": number,
  "damageStats": DamageStats,
  "goldPerSecond": number,
  "jungleMinionsKilled": number,
  "level": number,
  "minionsKilled": number,
  "participantId": number,
  "position": Position,
  "timeEnemySpentControlled": number,
  "totalGold": number,
  "xp": number
}
```

## Events

### PAUSE_END
```json
{ "realTimestamp": number, "timestamp": number, "type": "PAUSE_END" }
```

### ITEM_PURCHASED
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_PURCHASED" }
```

### ITEM_SOLD
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_SOLD" }
```

### ITEM_DESTROYED
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_DESTROYED" }
```

### ITEM_UNDO
```json
{ "afterId": number, "beforeId": number, "goldGain": number, "participantId": number, "timestamp": number, "type": "ITEM_UNDO" }
```

### SKILL_LEVEL_UP
```json
{ "levelUpType": string, "participantId": number, "skillSlot": number, "timestamp": number, "type": "SKILL_LEVEL_UP" }
```

### LEVEL_UP
```json
{ "level": number, "participantId": number, "timestamp": number, "type": "LEVEL_UP" }
```

### WARD_PLACED
```json
{ "creatorId": number, "timestamp": number, "type": "WARD_PLACED", "wardType": string }
```

### WARD_KILL
```json
{ "killerId": number, "timestamp": number, "type": "WARD_KILL", "wardType": string }
```

### CHAMPION_KILL
```json
{
  "assistingParticipantIds": [number],
  "bounty": number,
  "killStreakLength": number,
  "killerId": number,
  "position": Position,
  "shutdownBounty": number,
  "timestamp": number,
  "type": "CHAMPION_KILL",
  "victimDamageDealt": [DamageInstance],
  "victimDamageReceived": [DamageInstance],
  "victimId": number
}
```

### CHAMPION_SPECIAL_KILL
```json
{
  "killType": string,
  "killerId": number,
  "position": Position,
  "timestamp": number,
  "type": "CHAMPION_SPECIAL_KILL"
}
```

### ELITE_MONSTER_KILL
```json
{
  "killerTeamId": number,
  "monsterSubType": string,
  "monsterType": string,
  "position": Position,
  "timestamp": number,
  "type": "ELITE_MONSTER_KILL"
}
```

### BUILDING_KILL
```json
{
  "killerId": number,
  "laneType": string,
  "position": Position,
  "teamId": number,
  "timestamp": number,
  "towerType": string,
  "type": "BUILDING_KILL"
}
```

### TURRET_PLATE_DESTROYED
```json
{
  "killerId": number,
  "laneType": string,
  "position": Position,
  "teamId": number,
  "timestamp": number,
  "type": "TURRET_PLATE_DESTROYED"
}
```

### FEAT_UPDATE
```json
{ "featType": number, "featValue": number, "teamId": number, "timestamp": number, "type": "FEAT_UPDATE" }
```

### GAME_END
```json
{ "gameId": number, "realTimestamp": number, "timestamp": number, "type": "GAME_END", "winningTeam": number }
```

## Stats

### ChampionStats
```json
{
  "abilityHaste": number,
  "abilityPower": number,
  "armor": number,
  "armorPen": number,
  "armorPenPercent": number,
  "attackDamage": number,
  "attackSpeed": number,
  "bonusArmorPenPercent": number,
  "bonusMagicPenPercent": number,
  "ccReduction": number,
  "cooldownReduction": number,
  "health": number,
  "healthMax": number,
  "healthRegen": number,
  "lifesteal": number,
  "magicPen": number,
  "magicPenPercent": number,
  "magicResist": number,
  "movementSpeed": number,
  "omnivamp": number,
  "physicalVamp": number,
  "power": number,
  "powerMax": number,
  "powerRegen": number,
  "spellVamp": number
}
```

### DamageStats
```json
{
  "magicDamageDone": number,
  "magicDamageDoneToChampions": number,
  "magicDamageTaken": number,
  "physicalDamageDone": number,
  "physicalDamageDoneToChampions": number,
  "physicalDamageTaken": number,
  "totalDamageDone": number,
  "totalDamageDoneToChampions": number,
  "totalDamageTaken": number,
  "trueDamageDone": number,
  "trueDamageDoneToChampions": number,
  "trueDamageTaken": number
}
```

## Other

### Root
```json
{ "metadata": Metadata, "info": Info }
```

### Metadata
```json
{ "dataVersion": string, "matchId": string, "participants": [string] }
```

### Info
```json
{ "endOfGameResult": string, "frameInterval": number, "frames": [Frame] }
```

### Common Objects
```json
Position: { "x": number, "y": number }
DamageInstance: { "basic": boolean, "magicDamage": number, "name": string, "participantId": number, "physicalDamage": number, "spellName": string, "spellSlot": number, "trueDamage": number, "type": string }
```

