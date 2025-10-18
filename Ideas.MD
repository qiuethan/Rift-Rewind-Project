# API Info


## Goal
- Provide players with a concrete roadmap to improve their gameplay
- Recommend new champions
- Expand skills

### Scoping
- Summoner's Rift
- Web App
- User Flow (In Progress)
    - Get User's Games
    - Evaluate User's Performance
    - Provide Champion Recommendations
    - User Plays Champion
    - Evaluate User Performance on New Champion
    - Provide Feedback

#### Tasks:

(Based in General)

- Perform Champion Similarity Calculations
    - Scrape all Champions and Skills
    - Compare all Champions' Abilities to each other using LLM
    - Compare all Champions' Passives to each other using LLM
    - Compare all Champions' Stats (expand on this)
    - Find similar champions through player selection patterns (https://github.com/marlietandoc/lol)
    - Train ML model to cluster champions

- Create Play Evaluation Algorithm
    - Extract features from game timeline (JSON parsing)
    - Gold, CS, Deaths, KDA, Winrate, Damage
    - Extraction, analysis, synthesis of basic stats (tell a story of the data)
    - Evaluate performance of player

- UI/UX
    - Create web app
    - Create user flow
    - Create UI/UX
    - Display Basic Champion Information
        - Display champion information
        - Display champion combos
        - Display champion matchups
        - Display champion playstyle

### Brainstorm
- New champion recommendations
    - find champs close to recent champs / best champs
    - make analogies (ezreal q = lux q but faster)
    - scrape playstyles (farming junglers example)
    - find champions that players play - similar archetypes
    - do predictions on how well they will perform on that champion (clustering / euclidean distance problem?)
    - use gpt to calculate scores for similarity of abilities
    - use svm / clustering algorithm to calculate similarity of champions
    - using ml, figure out features to calculate champion similarity based on playstyle, stats
    - would be cool to find out overall stats from the champ (average cs, kills per minute etc etc) to calculate this champion similarity

- Key skills roadmap
    - you should play x champions to understand x fundamentals
    - learn what these champsions do so you know how to play against them
    - learn champs of similar playstyle (e.g. syndra, orianna) so you know how to play against mages
    - skills ladder
    - champion/role ladder - from a to c, a -> b -> c


## Ideas List

- CS/min but tracked every minute or 2 minutes (you can figure that out), (See if you farmed in midgame)
- Gold and xp difference at 10,15,20 etc minutes 
- Gank deaths per Laning phase, solo deaths per Laning deaths 
- Damage / tanking contribution in teamfights 
- CS lost in rotating to skirmish/teamfights (could also track gold and xp profit/loss) 
- Gold swing after objectives/teamfights (see if you used enemy death timers well)
- Good death vs bad death (gold value after death)








## Insights from Game Timeline

### PARTICIPANT FRAMES (ALL PLAYERS) - EVERY 60 SECONDS:
- "10" (participant ID)

#### Participant Object Keys:
- championStats
- currentGold
- damageStats
- goldPerSecond
- jungleMinionsKilled
- level
- minionsKilled
- participantId
- position
- timeEnemySpentControlled
- totalGold
- xp

#### championStats Keys:
- abilityHaste
- abilityPower
- armor
- armorPen
- armorPenPercent
- attackDamage
- attackSpeed
- bonusArmorPenPercent
- bonusMagicPenPercent
- ccReduction
- cooldownReduction
- health
- healthMax
- healthRegen
- lifesteal
- magicPen
- magicPenPercent
- magicResist
- movementSpeed
- omnivamp
- physicalVamp
- power
- powerMax
- powerRegen
- spellVamp

#### damageStats Keys:
- magicDamageDone
- magicDamageDoneToChampions
- magicDamageTaken
- physicalDamageDone
- physicalDamageDoneToChampions
- physicalDamageTaken
- totalDamageDone
- totalDamageDoneToChampions
- totalDamageTaken
- trueDamageDone
- trueDamageDoneToChampions
- trueDamageTaken

#### position Keys:
- x
- y

# Game events

Summary of event types and observed schemas from `riot_outputs/timeline_NA1_5377521793.json`.

## PAUSE_END
```json
{ "realTimestamp": number, "timestamp": number, "type": "PAUSE_END" }
```

## ITEM_PURCHASED
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_PURCHASED" }
```

## ITEM_SOLD
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_SOLD" }
```

## ITEM_DESTROYED
```json
{ "itemId": number, "participantId": number, "timestamp": number, "type": "ITEM_DESTROYED" }
```

## ITEM_UNDO
```json
{ "afterId": number, "beforeId": number, "goldGain": number, "participantId": number, "timestamp": number, "type": "ITEM_UNDO" }
```

## SKILL_LEVEL_UP
```json
{ "levelUpType": "NORMAL" | string, "participantId": number, "skillSlot": number, "timestamp": number, "type": "SKILL_LEVEL_UP" }
```

## LEVEL_UP
```json
{ "level": number, "participantId": number, "timestamp": number, "type": "LEVEL_UP" }
```

## WARD_PLACED
```json
{ "creatorId": number, "timestamp": number, "type": "WARD_PLACED", "wardType": "YELLOW_TRINKET" | "CONTROL_WARD" | "SIGHT_WARD" | "BLUE_TRINKET" | string }
```

## WARD_KILL
```json
{ "killerId": number, "timestamp": number, "type": "WARD_KILL", "wardType": "YELLOW_TRINKET" | "CONTROL_WARD" | "SIGHT_WARD" | "BLUE_TRINKET" | string }
```

## CHAMPION_KILL
```json
{
  "assistingParticipantIds": [number],
  "bounty": number,
  "killStreakLength": number,
  "killerId": number,
  "position": { "x": number, "y": number },
  "shutdownBounty": number,
  "timestamp": number,
  "type": "CHAMPION_KILL",
  "victimDamageDealt": [
    { "basic": boolean, "magicDamage": number, "name": string, "participantId": number, "physicalDamage": number, "spellName": string, "spellSlot": number, "trueDamage": number, "type": string }
  ],
  "victimDamageReceived": [ /* same shape as victimDamageDealt */ ],
  "victimId": number
}
```

## CHAMPION_SPECIAL_KILL
```json
{
  "killType": "KILL_FIRST_BLOOD" | "KILL_MULTI" | "KILL_ACE" | string,
  "killerId": number,
  "position": { "x": number, "y": number },
  "timestamp": number,
  "type": "CHAMPION_SPECIAL_KILL"
}
```

## ELITE_MONSTER_KILL
```json
{
  "killerTeamId": 100 | 200,
  "monsterSubType": "HEXTECH_DRAGON" | string,
  "monsterType": "DRAGON" | "BARON_NASHOR" | "RIFTHERALD" | "ELDER_DRAGON" | string,
  "position": { "x": number, "y": number },
  "timestamp": number,
  "type": "ELITE_MONSTER_KILL"
}
```

## BUILDING_KILL
```json
{
  "killerId": number,
  "laneType": "TOP_LANE" | "MID_LANE" | "BOT_LANE" | string,
  "position": { "x": number, "y": number },
  "teamId": 100 | 200,
  "timestamp": number,
  "towerType": "OUTER_TURRET" | "INNER_TURRET" | "BASE_TURRET" | "NEXUS_TURRET" | string,
  "type": "BUILDING_KILL"
}
```

## TURRET_PLATE_DESTROYED
```json
{
  "killerId": number,
  "laneType": "TOP_LANE" | "MID_LANE" | "BOT_LANE" | string,
  "position": { "x": number, "y": number },
  "teamId": 100 | 200,
  "timestamp": number,
  "type": "TURRET_PLATE_DESTROYED"
}
```

## FEAT_UPDATE
```json
{ "featType": number, "featValue": number, "teamId": 100 | 200, "timestamp": number, "type": "FEAT_UPDATE" }
```

## GAME_END
```json
{ "gameId": number, "realTimestamp": number, "timestamp": number, "type": "GAME_END", "winningTeam": 100 | 200 }
```

Notes:
- Values represent what was observed in this file; other matches may include additional variants.
- Team IDs: 100 = Blue, 200 = Red.