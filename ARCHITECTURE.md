# ARCHITECTURE.md

## What I Built

A browser-based player journey visualization tool for LILA BLACK telemetry data. A Level Designer can open it, select any match from 5 days of production data, and immediately see where players moved, where fights happened, where the storm killed people, and where loot was picked up — all overlaid on the actual minimap.

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Python + FastAPI | Fast to build, async-ready, auto-docs. Handles data processing cleanly. |
| Data reading | PyArrow + Pandas | Native parquet support. Pandas for aggregation and filtering. |
| Frontend | Vanilla HTML/JS + Canvas API | No build step, no framework overhead. Canvas gives pixel-level control for map rendering. Runs anywhere. |
| Image processing | Pillow | Resize large minimap images (up to 9000x9000px) to 1024x1024 before serving. |
| Hosting | Replit | Free, runs Python, serves HTTP, shareable URL out of the box. |

I deliberately avoided React/Vue because the tool is a single interactive view — no component hierarchy needed. Plain Canvas + vanilla JS is faster to load and easier to debug.

---

## Data Flow

```
.nakama-0 files (parquet)
        ↓
  PyArrow reads each file at startup
        ↓
  Pandas DataFrame (all events in memory, ~89k rows)
        ↓
  Pre-compute: pixel_x, pixel_y, is_bot flag, ts_ms, date
        ↓
  FastAPI REST endpoints serve filtered/aggregated JSON
        ↓
  Browser fetches match events via /api/match/<id>
        ↓
  Canvas API renders minimap + event markers + paths + heatmap
```

All data is loaded into memory at startup (~30-60 seconds). Subsequent queries are fast because everything is already in a Pandas DataFrame.

---

## Coordinate Mapping Approach

This was the trickiest part. The minimap images are top-down 2D renders of 3D game worlds. The game uses a standard 3D coordinate system (x, y, z) where y = elevation. For 2D minimap plotting, only x and z are used.

**The formula:**
```
u = (x - origin_x) / scale
v = (z - origin_z) / scale

pixel_x = u * 1024
pixel_y = (1 - v) * 1024     ← Y axis is FLIPPED
```

The Y flip is critical — image coordinates start at top-left (y=0 at top), but game world coordinates increase upward (z=0 at bottom). Without flipping, all events appear mirrored vertically.

**Map parameters (from README):**

| Map | Scale | Origin X | Origin Z |
|-----|-------|----------|----------|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

I verified these by sampling known events and confirming they land within minimap bounds (0-1024 range). Out-of-bounds events exist (players near map edges) but are handled gracefully — they simply render outside the visible canvas area.

The minimap images themselves vary in native resolution (AmbroseValley: 4320x4320, GrandRift: 2160x2158, Lockdown: 9000x9000). I normalize all to 1024x1024 on the backend using Pillow before base64-encoding for the frontend. This keeps the pixel math consistent across all maps.

---

## Assumptions

| Assumption | Reasoning |
|------------|-----------|
| `ts` column represents match-relative time, not wall-clock time | As documented in README. All timestamps start near epoch (1970-01-21), confirming they are offsets, not real dates. |
| Files with numeric user_id prefix are bots | Matches README definition. Validated: UUIDs are 36-char, numeric IDs are 4-digit numbers like "1440". |
| February 14 is a partial day | README states this. Handled by treating it the same as other days — just fewer matches. |
| `y` column = elevation, not map coordinate | README explicitly states this. Ignored for 2D plotting. |
| event column requires byte decoding | Stored as binary in parquet. Applied `.decode('utf-8')` on load. |

---

## Trade-offs

| Decision | What I chose | What I gave up |
|----------|-------------|----------------|
| All data in memory | Fast queries, no DB setup | ~200MB RAM usage at startup |
| Pre-compute pixel coords | Instant rendering | Slightly longer startup time |
| Vanilla JS canvas | No build step, fast load | Less component reuse than React |
| 1024x1024 minimap resize | Consistent math, smaller payload | Slight image quality loss for zoomed views |
| 64x64 heatmap grid | Smooth enough, fast to compute | Less granular than pixel-level heatmap |
| No user auth/sessions | Simple deployment | Not multi-user safe (fine for internal tool) |

---

## What I'd Do With More Time

1. **Add zoom + pan on the minimap** — currently the map fits the viewport. Zooming into high-density areas would help level designers inspect specific zones.
2. **Player path coloring by outcome** — color a player's path red if they died to the storm, green if they survived, etc.
3. **Side-by-side match comparison** — split screen to compare two matches on the same map.
4. **Export to image/video** — let a designer export a heatmap or timeline replay as a PNG or MP4.
5. **DuckDB instead of Pandas** — for much faster SQL-style queries on larger datasets without loading everything into memory.
6. **Persistent storage** — save analyst notes/annotations per match to a lightweight SQLite DB.
