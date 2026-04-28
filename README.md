# games-python

A collection of Python games.

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

```
pip install pygame
```

Python 3.8+ is required. No other third-party dependencies.

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
