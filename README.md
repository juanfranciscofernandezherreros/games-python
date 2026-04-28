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
