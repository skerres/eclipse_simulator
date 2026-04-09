# Eclipse: Second Dawn for the Galaxy — Battle Rules & Ship Configuration

## Overview

The **Combat Phase** resolves battles in sectors occupied by more than one opponent (players or NPCs such as Ancients, Guardians, or the GCDS). Battles are resolved in **descending sector number order** (the Galactic Center, sector 001, is always resolved last).

---

## Steps of Battle (per Sector)

1. **Determine order of battle resolution** — players battle two at a time in reverse order of entry into the sector.
2. **Determine Attacker and Defender** — based on reverse order of entry; the player who Controls the sector (has an Influence Disc) is always the Defender and battles last, regardless of entry order.
3. **Determine Initiative** for each Ship type.
4. **Fire Missiles** — fired once per battle, by Ship type, in Initiative order.
5. **Repeated Engagement Rounds** — until all of one player's Ships have Retreated or been destroyed.
6. **Draw Reputation Tiles** — after all battles in the sector are resolved, in order of entry.
7. **Return destroyed Ships** to their owners.

For battles with 3+ opponents, steps 1–5 repeat until a single opponent's Ships remain.

---

## Initiative

Initiative determines the activation order within each Engagement Round.

```
Initiative = Ship type's pre-printed Initiative Bonus
           + sum of all Initiative Symbols on Ship Parts on the Blueprint
```

- **Higher initiative activates first.**
- **Ties are resolved in the Defender's favor.**
- Initiative is calculated per Ship *type* (all Interceptors share one initiative value, all Cruisers another, etc.).

### Initiative Contributions from Ship Parts

| Part              | Initiative Bonus |
|-------------------|-----------------|
| Nuclear Drive     | +1              |
| Fusion Drive      | +2              |
| Tachyon Drive     | +3              |
| Transition Drive  | −1              |

---

## Engagement Rounds

Each Engagement Round, every Ship type of each player is activated in Initiative order. On activation, a Ship type must choose to either **Attack** or **Retreat**. Engagement Rounds repeat until all of one side's Ships have Retreated or been destroyed.

---

## Attacking

When a Ship type attacks:

1. **Roll dice** — roll one die of the corresponding color per Die Symbol on the Ship Blueprint, for **all Ships of that type simultaneously**.
   - Example: 3 Interceptors each with 1 Ion Cannon = roll 3 yellow dice.
   - Example: 1 Dreadnought with 2 Ion Cannons + 1 Plasma Cannon = roll 2 yellow + 1 orange dice.
2. **Assign dice** — after rolling, assign each die to a single enemy Ship. Multiple dice may target the same Ship.
3. **Determine hits** — check each die against the hit rules (see below).
4. **Apply damage** — for each hit, inflict damage based on the weapon type.

---

## Hitting

All four dice colors (yellow, orange, blue, red) function identically as d6. The color exists solely to track which weapon produced which result (since weapons deal different damage).

| Roll Result | Outcome |
|-------------|---------|
| **1** (blank face) | **Always a miss**, regardless of any bonuses |
| **6** (burst face) | **Always a hit**, regardless of any penalties |
| **2–5** | Hit if: `die roll + attacker's Computers − target's Shields ≥ 6` |

### Examples

- Die roll 4, attacker has Gluon Computer (+3), target has no shields: `4 + 3 − 0 = 7 ≥ 6` → **Hit**
- Die roll 3, attacker has Electron Computer (+1), target has Phase Shield (−2): `3 + 1 − 2 = 2 < 6` → **Miss**
- Die roll 5, attacker has Positron Computer (+2), target has Gauss Shield (−1): `5 + 2 − 1 = 6 ≥ 6` → **Hit**

### Minimum Roll to Hit (Reference Table)

Given `min_roll = 6 − computers + shields` (clamped to 2–6, since 1 always misses and 6 always hits):

| Computers − Shields | Min Roll | Hit Probability |
|---------------------|----------|-----------------|
| +5 or more          | 2 (always, except 1) | 5/6 ≈ 83.3% |
| +4                  | 2        | 5/6 ≈ 83.3%     |
| +3                  | 3        | 4/6 ≈ 66.7%     |
| +2                  | 4        | 3/6 = 50.0%     |
| +1                  | 5        | 2/6 ≈ 33.3%     |
| 0                   | 6 (only natural 6) | 1/6 ≈ 16.7% |
| −1 or less          | 6 (only natural 6) | 1/6 ≈ 16.7% |

---

## Damage

- Each hit inflicts damage equal to the **burst count** on the weapon's Die Symbol (printed on the Ship Part tile).
- A Ship is **destroyed** when total accumulated damage **exceeds** its **Hull Value** (total of all Hull symbols on the Blueprint).
  - A ship with 0 Hull is destroyed by 1 damage.
  - A ship with 2 Hull (e.g., one Improved Hull part) is destroyed by 3 damage.
- **Damage from a single die cannot be split** across multiple Ships (exception: Antimatter Splitter tech allows splitting Antimatter Cannon damage).
- Excess damage on a destroyed Ship does **not** carry over to other Ships.
- Undestroyed damage is tracked with purple **Damage Cubes** placed next to the Ship.
- All damage is **repaired** (Damage Cubes removed) at the end of the Combat Phase.

---

## Missiles

Missiles fire **once** at the very start of battle, before Engagement Rounds begin.

1. All Ship types with Missiles fire in **Initiative order**.
2. For each Plasma Missile part, roll **2 orange dice**.
3. For each Flux Missile part, roll **2 blue dice**.
4. Assign dice and resolve hits/damage using the normal rules.
5. Missiles are **not fired again** in subsequent Engagement Rounds.
6. Missiles **cannot** be used to attack population after battle.

---

## Retreat

- Instead of attacking, a Ship type may **Retreat** on its activation.
- Retreating Ships move to the **edge** of an adjacent sector that:
  - Contains the retreating player's Influence Disc
  - Does **not** contain enemy Ships
  - Is connected by a Wormhole
- While "on the edge," retreating Ships **can still be targeted and damaged**.
- On their **next activation**, retreating Ships complete the move and leave the battle.
- **Retreat penalty**: if all of a player's remaining Ships retreat, that player receives no Reputation Tile for participation (but still earns tiles for any enemy Ships destroyed).

---

## Stalemate

If a battle reaches a state where neither side can destroy the other (this can only happen when no Ships have Cannons), the **Attacker** may Retreat. If the Attacker cannot or does not Retreat, their Ships are destroyed.

---

## Non-Player Opponents (Ancients, Guardians, GCDS)

- NPCs are always considered **Defenders**.
- Another player rolls the dice for NPC attacks.
- NPC dice assignment rules (in priority order):
  1. Assign dice to **destroy the largest** player Ships first.
  2. If no Ships can be destroyed, assign to inflict **maximum damage to the largest** Ships first.

---

## Ship Types

| Ship Type       | Max per Player | Build Cost | Upgrade Slots | Initiative Bonus (Terran) | Notes |
|-----------------|---------------|------------|---------------|---------------------------|-------|
| **Interceptor** | 8             | 3 Materials | 4            | +2                        | Cheap, fast, expendable |
| **Cruiser**     | 4             | 5 Materials | 6            | +1                        | Balanced workhorse |
| **Dreadnought** | 2             | 8 Materials | 8            | 0                         | Heavy, many upgrade slots |
| **Starbase**    | 4             | 3 Materials | 5            | +4                        | Immobile, no Drives allowed |

### Blueprint Constraints

- **Energy**: total energy consumption of all Ship Parts must not exceed total energy production on the Blueprint.
- **Drives**: at least one Drive Ship Part tile must be present on Interceptor, Cruiser, and Dreadnought Blueprints. Drive tiles **cannot** be placed on Starbase Blueprints.
- **Upgrades are fleet-wide**: when a Blueprint is modified, all Ships of that type are instantly updated regardless of location.

---

## Ship Part Tiles

### Weapons

| Part | Die Color | Dice per Part | Damage per Hit | Energy Cost | Type | Tech Required |
|------|-----------|--------------|----------------|-------------|------|---------------|
| **Ion Cannon** | Yellow | 1 | 1 | 0 | Cannon | None (starting) |
| **Plasma Cannon** | Orange | 1 | 2 | 2 | Cannon | Plasma Cannon (Military) |
| **Soliton Cannon** | Orange | 1 | 3 | 1 | Cannon | Soliton Cannon (Rare) |
| **Antimatter Cannon** | Red | 1 | 4 | 2 | Cannon | Antimatter Cannon (Grid) |
| **Plasma Missile** | Orange | 2 | 2 each | 1 | Missile | Plasma Missile (Military) |
| **Flux Missile** | Blue | 2 | 3 each | 3 | Missile | Flux Missile (Rare) |

> **Rift Cannon** (expansion: Worlds Afar / Rift Cannon) — bypasses Computers and Shields but can backfire and damage your own Ships. Not part of the base game.

### Computers

| Part | Hit Bonus | Energy Cost | Tech Required |
|------|-----------|-------------|---------------|
| **Electron Computer** | +1 | 0 | None (starting) |
| **Positron Computer** | +2 | 1 | Positron Computer (Grid) |
| **Gluon Computer** | +3 | 2 | Gluon Computer (Military) |

### Shields

| Part | Shield Value | Energy Cost | Tech Required |
|------|-------------|-------------|---------------|
| **Gauss Shield** | −1 | 0 | Gauss Shield (Grid) |
| **Phase Shield** | −2 | 1 | Phase Shield (Military) |
| **Absorption Shield** | −1 | −4 (produces 4 energy) | Absorption Shield (Rare) |

### Hull

| Part | Hull Points | Energy Cost | Special | Tech Required |
|------|------------|-------------|---------|---------------|
| **Hull** | +1 | 0 | — | None (starting) |
| **Improved Hull** | +2 | 0 | — | Improved Hull (Grid) |
| **Sentient Hull** | +1 | 0 | Also acts as +1 Computer | Sentient Hull (Rare) |
| **Conifold Field** | +3 | 2 | — | Conifold Field (Rare) |

### Drives

Drives provide movement, initiative, and cost energy. Cannot be placed on Starbases. At least one required on all other ship types.

| Part | Move Value | Energy Cost | Initiative Bonus | Tech Required |
|------|-----------|-------------|-----------------|---------------|
| **Nuclear Drive** | 1 | 1 | +1 | None (starting) |
| **Fusion Drive** | 2 | 2 | +2 | Fusion Drive (Nano) |
| **Tachyon Drive** | 3 | 3 | +3 | Tachyon Drive (Grid) |
| **Transition Drive** | 3 | 0 | −1 | Transition Drive (Rare) |

### Energy Sources

| Part | Energy Production | Tech Required |
|------|-------------------|---------------|
| **Nuclear Source** | 3 | None (starting) |
| **Fusion Source** | 6 | Fusion Source (Grid) |
| **Tachyon Source** | 9 | Tachyon Source (Military) |
| **Zero-Point Source** | 12 | Zero-Point Source (Rare) |

---

## Default Terran Blueprints

### Interceptor

- **Initiative Bonus**: +2
- **Upgrade Slots**: 4 (2×2 grid)
- **Pre-printed Parts**: Ion Cannon, Nuclear Drive, Nuclear Source
- **Empty Slots**: 1
- **Starting Initiative**: 2 (bonus) + 1 (Nuclear Drive) = **3**
- **Starting Energy**: 3 produced − 1 consumed = **2 free**

### Cruiser

- **Initiative Bonus**: +1
- **Upgrade Slots**: 6 (2×3 grid)
- **Pre-printed Parts**: Ion Cannon, Electron Computer, Hull, Nuclear Drive, Nuclear Source
- **Empty Slots**: 1
- **Starting Initiative**: 1 (bonus) + 1 (Nuclear Drive) = **2**
- **Starting Energy**: 3 produced − 1 consumed = **2 free**

### Dreadnought

- **Initiative Bonus**: 0
- **Upgrade Slots**: 8 (2×4 grid)
- **Pre-printed Parts**: Ion Cannon ×2, Hull, Nuclear Drive, Nuclear Source
- **Empty Slots**: 3
- **Starting Initiative**: 0 (bonus) + 1 (Nuclear Drive) = **1**
- **Starting Energy**: 3 produced − 1 consumed = **2 free**

### Starbase

- **Initiative Bonus**: +4
- **Upgrade Slots**: 5
- **Pre-printed Parts**: Ion Cannon, Nuclear Source
- **Empty Slots**: 3 (no Drives allowed)
- **Starting Initiative**: **4**
- **Starting Energy**: 3 produced − 0 consumed = **3 free**

---

## Non-Player Ship Blueprints

### Ancient Ship

| Property | Value |
|----------|-------|
| Weapons  | 2× Ion Cannon (2 yellow dice, 1 damage each) |
| Computer | Electron Computer (+1) |
| Hull     | 1 (destroyed by 2 damage) |
| Initiative | 2 |

### Guardian Ship

Stronger than Ancients. Specific Blueprint Tile is chosen during setup (standard or advanced variant). Stats vary by tile.

### Galactic Center Defense System (GCDS)

| Property | Value |
|----------|-------|
| Weapons  | 4× Ion Cannon (4 yellow dice, 1 damage each) |
| Computer | Electron Computer (+1) |
| Hull     | 7 (destroyed by 8 damage) |
| Initiative | 0 |

---

## Combat-Relevant Technologies (Non-Ship-Part)

| Tech | Effect |
|------|--------|
| **Neutron Bombs** | Destroy all enemy Population Cubes in a sector automatically (no dice roll) |
| **Antimatter Splitter** | Damage from Antimatter Cannons may be split across multiple target Ships |
| **Cloaking Device** | Opponents cannot target specific Ships during combat |
| **Neutron Absorber** | Each of your Ships absorbs 1 extra damage (effectively +1 Hull on all Ships) |

---

## Reputation Tiles (Combat Rewards)

After all battles in a sector are resolved, each participating player draws Reputation Tiles:

| Condition | Tiles Drawn |
|-----------|-------------|
| Participated in one or more battles | 1 |
| Per enemy Interceptor destroyed | 1 |
| Per enemy Starbase destroyed | 1 |
| Per Ancient Ship destroyed | 1 |
| Per enemy Cruiser destroyed | 2 |
| Per enemy Dreadnought destroyed | 3 |
| GCDS destroyed | 3 |

- Maximum **5 tiles** drawn per player per sector.
- Choose **1 tile** to keep, return the rest to the bag.
- Tiles are worth 1–4 VP each (drawn blind from bag).

---

## Simulator-Relevant Summary

For the purpose of simulating a battle, the key inputs per side are:

1. **Fleet composition**: list of Ships with their Blueprint configurations.
2. **Per Ship type**: weapons (dice color + damage), computer total, shield total, hull total, initiative total.
3. **Attacker/Defender designation** (affects tie-breaking).

The simulation loop is:

```
1. MISSILE PHASE (once)
   For each Ship type with missiles, in initiative order:
     - Roll missile dice
     - Assign to enemy ships (optimally or randomly)
     - Resolve hits and damage
     - Remove destroyed ships

2. ENGAGEMENT ROUNDS (repeat until one side eliminated)
   For each Ship type across both sides, in initiative order:
     - Choose: Attack or Retreat
     - If Attack:
       - Roll cannon dice for all ships of this type
       - Assign dice to enemy ships
       - Resolve hits and damage
       - Remove destroyed ships
     - If Retreat:
       - Mark as retreating (still targetable this round)
       - Remove from battle on next activation
```

### Dice Assignment Strategy (for simulator)

The simulator needs a strategy for assigning dice to targets. Options:

- **Optimal**: assign dice to maximize expected damage / ship kills (computationally expensive).
- **Greedy**: assign each die to the enemy ship it is most likely to destroy.
- **Random**: assign dice randomly (useful as a baseline).
- **NPC rules**: largest-to-smallest destruction priority (as specified in the rules for Ancients/Guardians/GCDS).

---

## Caveats

- Some exact stat values for rare Ship Parts (Soliton Cannon, Flux Missile, Conifold Field, etc.) should be verified against the physical tiles. The values above are compiled from the rulebook, Dized rules, BGG community sources, and Eclipse wiki.
- Species-specific Blueprint variations (Eridani Empire, Hydran Progress, Planta, Descendants of Draco, Mechanema, Orion Hegemony) differ from the Terran defaults and are not detailed here.
- The Rift Cannon expansion introduces unique mechanics (bypassing computers/shields, backfire risk) not covered above.
