# LILA BLACK — Player Journey Visualization Tool

## Overview
A browser-based internal utility for level designers of the game *LILA BLACK*. Visualizes player movement and behavior across game maps (AmbroseValley, GrandRift, Lockdown) using production telemetry data.

## Tech Stack
- **Backend:** Python 3.12, FastAPI, Uvicorn, Gunicorn
- **Frontend:** Vanilla HTML5, CSS, JavaScript (Canvas API) — served as static file from FastAPI
- **Data Processing:** Pandas, PyArrow (reads `.nakama-0` Parquet files), NumPy
- **Image Processing:** Pillow (resizes minimaps to 1024x1024)

## Project Structure
```
main.py           # FastAPI backend: data pipeline, API endpoints, static server
index.html        # Frontend: unified HTML/JS/CSS using Canvas API
requirements.txt  # Python dependencies
player_data/      # Expected directory (NOT in repo — must be uploaded):
  February_*/     # Daily telemetry folders containing .nakama-0 Parquet files
  minimaps/       # Minimap images (AmbroseValley_Minimap.png, GrandRift_Minimap.png, Lockdown_Minimap.jpg)
```

## Running the App
- **Development:** `python main.py` — runs on port 5000
- **Production:** Gunicorn with UvicornWorker on port 5000 (1 worker — app holds data in memory)

## Key Notes
- The app loads all telemetry data into memory at startup (can take 30-60 seconds with data)
- Without `player_data/`, the app runs but shows no data — this is expected
- Must use 1 Gunicorn worker (vm deployment) since data is stored in global memory
- Port: 5000

## API Endpoints
- `GET /` — serves index.html frontend
- `GET /api/maps` — list of available maps
- `GET /api/dates` — list of available dates
- `GET /api/matches?map=&date=` — match list with stats
- `GET /api/match/{match_id}` — events for a specific match
- `GET /api/heatmap?map=&event_type=` — heatmap grid data
- `GET /api/minimap/{map_id}` — base64-encoded minimap image
- `GET /api/stats` — overall statistics
