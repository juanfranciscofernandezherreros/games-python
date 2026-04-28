import socket
import sys
import threading

# Network configuration
# Binds to all interfaces intentionally so remote clients can connect.
SERVER = "0.0.0.0"
PORT = 5555
MAX_PLAYERS = 2

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind((SERVER, PORT))
except socket.error as e:
    print(str(e))
    sys.exit(1)

server_socket.listen(MAX_PLAYERS)
print("Waiting for connections... Server started")

# Initial player state (x, y, character name)
pos = [
    {"x": 50,  "y": 400, "char": "Mario"},
    {"x": 100, "y": 400, "char": "Luigi"},
]

lock = threading.Lock()


def threaded_client(conn, player):
    # Send "player_index,x,y" so the client knows its identity
    with lock:
        initial = f"{player},{pos[player]['x']},{pos[player]['y']}"
    conn.send(initial.encode("utf-8"))

    while True:
        try:
            data = conn.recv(2048).decode("utf-8")
            if not data:
                print(f"Player {player} disconnected")
                break

            # Validate and update the global position for this player
            coords = data.split(",")
            if len(coords) != 2:
                continue
            try:
                new_x, new_y = int(coords[0]), int(coords[1])
            except ValueError:
                continue

            with lock:
                pos[player]["x"] = new_x
                pos[player]["y"] = new_y

                # Reply with the OTHER player's position
                enemy = 1 if player == 0 else 0
                reply = f"{pos[enemy]['x']},{pos[enemy]['y']}"

            conn.sendall(reply.encode("utf-8"))
        except Exception as e:
            print(f"Error for player {player}: {e}")
            break

    print(f"Player {player} connection closed")
    conn.close()


curr_player = 0
client_threads = []
while curr_player < MAX_PLAYERS:
    conn, addr = server_socket.accept()
    print(f"Connected to: {addr}  (player {curr_player})")
    t = threading.Thread(target=threaded_client, args=(conn, curr_player), daemon=True)
    t.start()
    client_threads.append(t)
    curr_player += 1

# Block until all client threads finish (both players disconnected)
for t in client_threads:
    t.join()
print("All players disconnected. Server shutting down.")
