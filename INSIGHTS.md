# INSIGHTS.md

Three insights derived from exploring 89,104 events across 796 matches (Feb 10–14, 2026) using the visualization tool.

---

## Insight 1: PvP Combat Is Nearly Absent — Bots Are Doing Almost All the Fighting

**What I noticed:**
When filtering the match view to show only Kill/Killed events, almost nothing appeared. Switching to BotKill/BotKilled events filled the map. I ran the numbers to confirm.

**The data:**
- PvP kills (human kills human): **3 total** across all 5 days and 796 matches
- Bot kills (human kills bot): **2,415**
- Ratio: **~600 bot kills for every 1 PvP kill**
- Human players who died to another human: only **3 unique players**
- Human players who died to a bot: **700 events**

**What this means for a level designer:**
The current map design is being stress-tested almost entirely through human-vs-bot encounters, not PvP. Combat zones, chokepoints, and cover placement are being evaluated by bot behavior — not human decision-making. Any level design assumptions built around "where will players fight each other" have essentially zero real data to validate against.

**Actionable items:**
- Flag PvP kill zone design as unvalidated until real player-vs-player data exists
- Consider whether bot pathing is representative of human routing through the maps
- Metrics to watch: PvP kill count, PvP kill/death ratio by zone, average time-to-first-PvP-contact per match

---

## Insight 2: AmbroseValley Has a Single Dominant Traffic Corridor — 27% of All Movement Funnels Through 5 Grid Zones

**What I noticed:**
Loading the heatmap overlay (Player Traffic) on AmbroseValley showed one intensely bright cluster rather than distributed movement across the map. The map is large but players are not using most of it.

**The data:**
- AmbroseValley had 566 matches — by far the most played map (GrandRift: 59, Lockdown: 171)
- Dividing the map into a 10×10 grid, the top 5 cells (out of 100) account for **26.8% of all movement**
- The single hottest cell (center-right of map, grid position 5,4) alone contains **3,219 position samples** — nearly 2× the next busiest cell
- Average loot per match on AmbroseValley: **18.5 events** vs 14.3 on Lockdown

**What this means for a level designer:**
The majority of the map is effectively dead space. Players are routing through predictable corridors, likely driven by terrain or loot placement. The outer quadrants of the map have very low traffic, meaning those areas' design effort isn't being experienced. This also creates predictability — experienced players can camp the hot corridor.

**Actionable items:**
- Investigate what's drawing players to the high-traffic zones: is it loot spawns, terrain openness, or shortest path to extraction?
- Add secondary loot incentives or alternate extraction points in low-traffic quadrants to widen player distribution
- Metrics to watch: traffic distribution entropy (how evenly spread is movement), loot-pickup density per zone, storm death locations relative to traffic corridors

---

## Insight 3: Storm Deaths Are Concentrated Near Map Center, Suggesting Players Are Caught Mid-Rotation — Not at the Edge

**What I noticed:**
Enabling the Storm Deaths heatmap overlay showed deaths clustering near the middle of each map rather than at the periphery. This was counterintuitive — I expected storm deaths to happen at the map edges where players get caught outside the zone.

**The data:**
- Total storm deaths across all maps: **39 events**
- AmbroseValley storm deaths: 17, mean position (x=20, z=−30) — near map center
- Lockdown storm deaths: 17, mean position (x=49, z=44) — also near center
- GrandRift storm deaths: 5, mean position (x=4, z=4) — exactly at center

**What this means for a level designer:**
Players aren't dying at the map edge as the storm approaches — they're dying in the middle of the map, likely during active combat or loot collection when they lose track of the storm boundary. This suggests either the storm timing is too aggressive for players who are engaged, or the visual storm warning cues are insufficient while in combat.

**Actionable items:**
- Test storm warning visibility during combat scenarios — are UI indicators getting lost in the action?
- Consider whether the storm speed in Lockdown (a smaller/faster map) is appropriately tuned given 17 storm deaths match AmbroseValley despite far fewer matches
- Metrics to watch: average distance from storm boundary at time of storm death, correlation between nearby combat events and storm death events (dying while fighting = missed warning), storm death rate per match by map
