"""
web_server.py — FastAPI WebSocket server for Mario & Luigi Multiplayer (web edition).

Serves the static HTML frontend and manages room-based multiplayer:
  - Up to 2 players per room.
  - Each player sends {"x": <int>, "y": <int>} every frame.
  - The server stores both positions and echoes the *opponent's* position back.

Run with:
    uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mario & Luigi Web Multiplayer")

STATIC_DIR = Path(__file__).parent / "static"

# Serve index.html at the root
@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

# Serve other static assets (CSS, JS, images if any)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Room management
# ---------------------------------------------------------------------------

INITIAL_POSITIONS = [
    {"x": 50,  "y": 400},
    {"x": 150, "y": 400},
]

# rooms[room_id] = list of up to 2 WebSocket connections
rooms: dict[str, list[Optional[WebSocket]]] = {}

# rooms_pos[room_id] = list of 2 position dicts {"x": int, "y": int}
rooms_pos: dict[str, list[dict]] = {}


def _get_or_create_room(room_id: str) -> list[Optional[WebSocket]]:
    if room_id not in rooms:
        rooms[room_id] = [None, None]
        rooms_pos[room_id] = [
            dict(INITIAL_POSITIONS[0]),
            dict(INITIAL_POSITIONS[1]),
        ]
    return rooms[room_id]


def _assign_slot(room_id: str) -> Optional[int]:
    """Return the first free slot index (0 or 1), or None if the room is full."""
    for i, ws in enumerate(rooms[room_id]):
        if ws is None:
            return i
    return None


def _cleanup_room(room_id: str, slot: int) -> None:
    if room_id in rooms:
        rooms[room_id][slot] = None
        # Remove room entirely if both players have left
        if all(ws is None for ws in rooms[room_id]):
            del rooms[room_id]
            del rooms_pos[room_id]
            logger.info("Room '%s' removed (empty).", room_id)


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str) -> None:
    await websocket.accept()

    _get_or_create_room(room_id)
    slot = _assign_slot(room_id)

    if slot is None:
        await websocket.send_json({"type": "error", "message": "Room is full"})
        await websocket.close()
        return

    rooms[room_id][slot] = websocket
    init_pos = rooms_pos[room_id][slot]
    await websocket.send_json({
        "type": "init",
        "player_index": slot,
        "x": init_pos["x"],
        "y": init_pos["y"],
    })
    logger.info("Player %d joined room '%s'.", slot, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Update this player's stored position
            new_x = int(payload.get("x", rooms_pos[room_id][slot]["x"]))
            new_y = int(payload.get("y", rooms_pos[room_id][slot]["y"]))
            rooms_pos[room_id][slot]["x"] = new_x
            rooms_pos[room_id][slot]["y"] = new_y

            # Send back the *opponent's* current position
            opponent = 1 - slot
            opp_ws = rooms[room_id][opponent]
            opp_pos = rooms_pos[room_id][opponent]

            reply = {
                "type": "update",
                "x": opp_pos["x"],
                "y": opp_pos["y"],
                "connected": opp_ws is not None,
            }
            await websocket.send_json(reply)

    except WebSocketDisconnect:
        logger.info("Player %d left room '%s'.", slot, room_id)
    except Exception as exc:
        logger.error("Unexpected error for player %d in room '%s': %s", slot, room_id, exc)
    finally:
        _cleanup_room(room_id, slot)
