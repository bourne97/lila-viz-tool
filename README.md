# LILA BLACK — Player Journey Visualization Tool

A browser-based tool for LILA BLACK level designers to explore player behavior across 5 days of production telemetry data.

**Live URL:** *(add your Replit deployment URL here)*

---

## Features

- 🗺 **Minimap rendering** — Player events plotted on actual game minimaps (AmbroseValley, GrandRift, Lockdown)
- 👤 **Human vs Bot distinction** — Humans as circles, bots as triangles, different colors
- 🎯 **Event markers** — Kill, Death, BotKill, BotKilled, Storm Death, Loot — each with distinct visual
- 🔍 **Filters** — Filter by map, date, match, and event type
- ⏱ **Timeline playback** — Scrub or auto-play through a match chronologically
- 🌡 **Heatmaps** — Kill zones, death zones, loot density, player traffic overlays
- 📊 **Match summary** — Instant stats per match (kills, deaths, storm deaths, loot)

---

## Setup (Local)

### Requirements
- Python 3.10+
- ~500MB RAM (data loads into memory)

### Steps

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd lila-viz-tool

# 2. Unzip data into project root
unzip player_data.zip
# You should now have: player_data/February_10/ ... February_14/ minimaps/

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python main.py

# 5. Open in browser
# http://localhost:8080
```

---

## Setup (Replit)

1. Create a new **Python** Repl on replit.com
2. Upload `player_data.zip` into the Repl file panel
3. Open the Shell and run:
   ```bash
   unzip player_data.zip
   pip install -r requirements.txt
   ```
4. Set the **Run** command to: `python main.py`
5. Click **Run** — the tool will be available at your Replit URL

> **Note:** First startup takes 30–60 seconds to load all parquet files. Subsequent API calls are fast.

---

## Project Structure

```
lila-viz-tool/
├── main.py           # FastAPI backend — data pipeline + REST API
├── index.html        # Frontend — minimap canvas, filters, timeline, heatmap
├── requirements.txt  # Python dependencies
├── README.md         # This file
├── ARCHITECTURE.md   # Tech decisions, data flow, coordinate mapping
├── INSIGHTS.md       # 3 actionable level design insights from the data
└── player_data/      # (unzipped) telemetry data + minimap images
    ├── February_10/
    ├── February_11/
    ├── February_12/
    ├── February_13/
    ├── February_14/
    └── minimaps/
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/maps` | List of available maps |
| `GET /api/dates` | List of available dates |
| `GET /api/matches?map=X&date=Y` | Matches filtered by map/date |
| `GET /api/match/<match_id>` | All events for a match with pixel coords |
| `GET /api/heatmap?map=X&event_type=Y` | Heatmap grid data |
| `GET /api/minimap/<map_id>` | Base64-encoded minimap image |
| `GET /api/stats` | Global dataset statistics |

---

## Environment Variables

None required. The tool runs fully self-contained.

---

## Tech Stack

- **Backend:** Python, FastAPI, PyArrow, Pandas, Pillow
- **Frontend:** Vanilla HTML/JS, Canvas API
- **Hosting:** Replit (or any Python host)
