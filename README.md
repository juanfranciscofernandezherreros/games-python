# games-python

A collection of Python games.

---

## Environment Setup

### Requirements

* **Python 3.8+** — [Download](https://www.python.org/downloads/)
* **pygame 2.1+**

### Quick install (recommended: use a virtual environment)

```bash
# 1. Clone the repository
git clone https://github.com/juanfranciscofernandezherreros/games-python.git
cd games-python

# 2. Create and activate a virtual environment
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (cmd):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

> **Linux note:** pygame requires a display server and some system libraries.
> Install them with:
> ```bash
> sudo apt-get install python3-dev libsdl2-dev libsdl2-image-dev \
>     libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev
> ```

> **macOS note:** If you install Python via Homebrew, make sure you use the
> Homebrew Python and not the system one:
> ```bash
> brew install python
> ```

---

## Mario & Luigi Multiplayer

A basic two-player side-scrolling platformer built with **pygame** and Python
**sockets** (TCP). One machine runs the server; each player runs a client.

### Architecture

```
[Client 1 – Mario]  <──TCP──>  [Server]  <──TCP──>  [Client 2 – Luigi]
  sends x,y                    game state               sends x,y
  receives opponent x,y        source of truth          receives opponent x,y
```

The server is the authoritative source of truth: it receives each player's
position, stores it, and replies with the other player's position.
Each client handles its own physics (gravity, jumping) locally and sends
the result to the server every frame.

### Requirements

See the **Environment Setup** section at the top of this file.

### How to run

**Step 1 – Start the server** (run this first, on any machine):

```bash
python server.py
```

The server listens on `0.0.0.0:5555` and waits for two clients.

**Step 2 – Start the clients** (run on two separate terminals / machines):

```bash
python client.py
```

By default `client.py` connects to `localhost`. To connect to a remote
server change `SERVER_IP` at the top of `client.py`.

### Controls

| Key | Action |
|-----|--------|
| ← / → | Move left / right |
| ↑ or Space | Jump |
| Esc | Quit |

### Files

| File | Description |
|------|-------------|
| `server.py` | TCP server — manages shared game state |
| `client.py` | Pygame client — input, physics, rendering |

---

## Mario & Luigi Local Multiplayer

A standalone local two-player platformer. Both players share the same
screen and keyboard — no network connection needed.

### Features

* Ground tiles, floating brick/question/stone blocks, pipes, and clouds
* Score and lives HUD displaying real-time player positions
* Pixel-art sprite support via an `assets/` folder (color-block placeholders
  are used automatically when image files are missing)

### How to run

```bash
python game_local.py
```

### Controls

| Player | Key | Action |
|--------|-----|--------|
| P1 – Mario | ← / → | Move left / right |
| P1 – Mario | ↑ | Jump |
| P2 – Luigi | A / D | Move left / right |
| P2 – Luigi | W | Jump |
| Both | Esc | Quit |

### Optional assets

Place image files in an `assets/` sub-folder to replace the color
placeholders:

| File | Description |
|------|-------------|
| `mario_walk.png` | Mario sprite |
| `luigi_stand.png` | Luigi sprite |
| `brick_block.png` | Brick block tile |
| `question_block.png` | Question-mark block tile |
| `stone_block.png` | Stone block tile |
| `ground_brick.png` | Ground tile |
| `cloud.png` | Cloud sprite |
| `pipe.png` | Pipe sprite |

A `PressStart2P.ttf` font file placed in the same directory as
`game_local.py` will be used for the HUD text if available.

---

## Web Edition (HTML5 Canvas)

A browser-based version that reproduces both game modes — no Pygame required.

### Architecture

```
Browser  ──HTTP──>  FastAPI (web_server.py)  serves  static/index.html
Browser  ──WS───>  /ws/{room_id}            WebSocket multiplayer relay
```

### Files

| File | Description |
|------|-------------|
| `web_server.py` | FastAPI server — serves the frontend and relays multiplayer positions |
| `static/index.html` | Self-contained HTML5 Canvas game (local & multiplayer modes) |
| `Procfile` | Heroku process declaration |
| `runtime.txt` | Python version pin for Heroku |

### Run locally

```bash
# Install dependencies (includes fastapi & uvicorn)
pip install -r requirements.txt

# Start the server
uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000** in your browser.

### Controls (web)

| Mode | Player | Keys | Action |
|------|--------|------|--------|
| Local | P1 – Mario | ← → ↑ / Space | Move & jump |
| Local | P2 – Luigi | A D W | Move & jump |
| Multiplayer | Your character | ← → ↑ / Space | Move & jump |

### Multiplayer (same network or remote)

1. Start the server (see above, or deploy to Heroku).
2. Both players open the game URL in their browser.
3. Click **Multiplayer**, type the **same Room ID**, and click **Connect**.
4. The first to connect becomes Mario; the second becomes Luigi.

---

## Deploy to Heroku

### Prerequisites

* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed and logged in (`heroku login`).
* Git repository initialised (already done if you cloned this repo).

### Steps

```bash
# 1. Create a new Heroku app (choose any name, or omit for a random one)
heroku create your-app-name

# 2. Push to Heroku
git push heroku main

# 3. Open the deployed app in your browser
heroku open
```

The `Procfile` already tells Heroku to start uvicorn and bind to the
`$PORT` environment variable that Heroku provides automatically.

### Notes

* Heroku requires a paid dyno type (free dynos were discontinued in
  November 2022). The cheapest option is the **Eco** dyno plan.
* Eco dynos sleep after 30 minutes of inactivity — the first
  request after sleep takes a few seconds.
* WebSockets are fully supported on Heroku (all dynos).
* If you use multiple dynos, add a Redis-backed session store so room state
  is shared across instances (the current in-memory store works on a single
  dyno).
