import os, zipfile, io
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# ─── Map configuration ───────────────────────────────────────────────────────
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

MINIMAP_SIZE = 1024  # We'll serve minimaps resized to 1024

# ─── Global data store ───────────────────────────────────────────────────────
DATA: pd.DataFrame = pd.DataFrame()
MINIMAP_B64: dict = {}

def world_to_pixel(x, z, map_id):
    cfg = MAP_CONFIG[map_id]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * MINIMAP_SIZE
    py = (1 - v) * MINIMAP_SIZE
    return round(float(px), 1), round(float(py), 1)

def load_all_data():
    global DATA
    data_dir = "player_data"
    if not os.path.exists(data_dir):
        print("ERROR: player_data folder not found. Please unzip player_data.zip first.")
        return

    frames = []
    date_folders = [d for d in os.listdir(data_dir)
                    if os.path.isdir(os.path.join(data_dir, d)) and d.startswith("February")]

    total = 0
    for folder in sorted(date_folders):
        folder_path = os.path.join(data_dir, folder)
        files = [f for f in os.listdir(folder_path) if f.endswith(".nakama-0")]
        print(f"Loading {folder}: {len(files)} files...")
        for fname in files:
            fpath = os.path.join(folder_path, fname)
            try:
                df = pq.read_table(fpath).to_pandas()
                df["event"] = df["event"].apply(
                    lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
                )
                df["date"] = folder
                df["is_bot"] = df["user_id"].str.match(r"^\d+$")
                frames.append(df)
                total += len(df)
            except Exception as e:
                pass  # skip corrupt files

    if not frames:
        print("No data loaded.")
        return

    DATA = pd.concat(frames, ignore_index=True)

    # Pre-compute pixel coordinates
    px_list, py_list = [], []
    for _, row in DATA.iterrows():
        map_id = row["map_id"]
        if map_id in MAP_CONFIG:
            px, py = world_to_pixel(row["x"], row["z"], map_id)
        else:
            px, py = 0, 0
        px_list.append(px)
        py_list.append(py)
    DATA["px"] = px_list
    DATA["py"] = py_list

    # Clean up match_id (strip .nakama-0 suffix for display)
    DATA["match_id_clean"] = DATA["match_id"].str.replace(r"\.nakama-0$", "", regex=True)

    # ts to ms integer for timeline
    DATA["ts_ms"] = DATA["ts"].astype(np.int64) // 1_000_000

    print(f"✓ Loaded {total:,} events from {len(frames)} files")
    print(f"  Maps: {DATA['map_id'].unique().tolist()}")
    print(f"  Dates: {sorted(DATA['date'].unique().tolist())}")


def load_minimaps():
    global MINIMAP_B64
    import base64
    from PIL import Image

    minimap_dir = os.path.join("player_data", "minimaps")
    if not os.path.exists(minimap_dir):
        print("Minimaps folder not found.")
        return

    map_files = {
        "AmbroseValley": "AmbroseValley_Minimap.png",
        "GrandRift":     "GrandRift_Minimap.png",
        "Lockdown":      "Lockdown_Minimap.jpg",
    }
    for map_id, fname in map_files.items():
        fpath = os.path.join(minimap_dir, fname)
        if os.path.exists(fpath):
            img = Image.open(fpath).convert("RGB")
            img = img.resize((MINIMAP_SIZE, MINIMAP_SIZE), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            MINIMAP_B64[map_id] = f"data:image/jpeg;base64,{b64}"
            print(f"✓ Minimap loaded: {map_id}")


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.get("/api/maps")
def get_maps():
    if DATA.empty:
        return []
    return sorted(DATA["map_id"].unique().tolist())

@app.get("/api/dates")
def get_dates():
    if DATA.empty:
        return []
    return sorted(DATA["date"].unique().tolist())

@app.get("/api/matches")
def get_matches(map: str = None, date: str = None):
    if DATA.empty:
        return []
    df = DATA.copy()
    if map:
        df = df[df["map_id"] == map]
    if date:
        df = df[df["date"] == date]
    # Return match list with summary stats
    matches = []
    for mid, grp in df.groupby("match_id_clean"):
        humans = grp[~grp["is_bot"]]["user_id"].nunique()
        bots   = grp[grp["is_bot"]]["user_id"].nunique()
        kills  = len(grp[grp["event"].isin(["Kill", "Killed", "BotKill", "BotKilled"])])
        matches.append({
            "match_id": mid,
            "full_match_id": grp["match_id"].iloc[0],
            "map": grp["map_id"].iloc[0],
            "date": grp["date"].iloc[0],
            "humans": int(humans),
            "bots": int(bots),
            "events": int(len(grp)),
            "kills": int(kills),
        })
    matches.sort(key=lambda x: x["events"], reverse=True)
    return matches[:200]  # cap at 200 matches

@app.get("/api/match/{match_id_clean}")
def get_match_events(match_id_clean: str, event_types: str = None):
    if DATA.empty:
        return []
    df = DATA[DATA["match_id_clean"] == match_id_clean].copy()
    if event_types:
        types = event_types.split(",")
        df = df[df["event"].isin(types)]
    df = df.sort_values("ts_ms")

    # Normalize ts to start from 0
    if not df.empty:
        min_ts = df["ts_ms"].min()
        df["ts_rel"] = (df["ts_ms"] - min_ts).astype(int)
    else:
        df["ts_rel"] = 0

    cols = ["user_id", "is_bot", "event", "px", "py", "ts_rel"]
    return df[cols].to_dict(orient="records")

@app.get("/api/heatmap")
def get_heatmap(map: str = "AmbroseValley", event_type: str = "Kill"):
    if DATA.empty:
        return {"grid": [], "max": 0}
    df = DATA[(DATA["map_id"] == map) & (DATA["event"] == event_type)]
    if df.empty:
        return {"grid": [], "max": 0}

    # Build a 64x64 grid
    grid_size = 64
    cell = MINIMAP_SIZE / grid_size
    grid = np.zeros((grid_size, grid_size), dtype=int)
    for _, row in df.iterrows():
        gx = int(min(row["px"] / cell, grid_size - 1))
        gy = int(min(row["py"] / cell, grid_size - 1))
        if 0 <= gx < grid_size and 0 <= gy < grid_size:
            grid[gy][gx] += 1

    points = []
    for gy in range(grid_size):
        for gx in range(grid_size):
            if grid[gy][gx] > 0:
                points.append({
                    "x": int(gx * cell + cell / 2),
                    "y": int(gy * cell + cell / 2),
                    "value": int(grid[gy][gx])
                })
    max_val = int(grid.max()) if grid.max() > 0 else 1
    return {"grid": points, "max": max_val}

@app.get("/api/minimap/{map_id}")
def get_minimap(map_id: str):
    if map_id not in MINIMAP_B64:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"data": MINIMAP_B64[map_id]}

@app.get("/api/stats")
def get_stats():
    if DATA.empty:
        return {}
    return {
        "total_events": int(len(DATA)),
        "total_matches": int(DATA["match_id"].nunique()),
        "total_players": int(DATA[~DATA["is_bot"]]["user_id"].nunique()),
        "total_bots": int(DATA[DATA["is_bot"]]["user_id"].nunique()),
        "maps": DATA["map_id"].value_counts().to_dict(),
        "events": DATA["event"].value_counts().to_dict(),
    }

# ─── Serve frontend ───────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("index.html", "r") as f:
        return f.read()

# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    print("Loading minimap images...")
    load_minimaps()
    print("Loading player data (this may take 30-60 seconds)...")
    load_all_data()
    print("Ready!")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=False)
