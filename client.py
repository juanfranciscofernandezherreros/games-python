import pygame
import socket
import sys

# ── Window & physics constants ──────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
GROUND_Y = 480          # y-coordinate of the ground surface
PLAYER_W, PLAYER_H = 40, 60

# ── Colours ──────────────────────────────────────────────────────────────────
SKY_BLUE    = (135, 206, 235)
GROUND_CLR  = (139,  90,  43)
MARIO_CLR   = (255,   0,   0)   # red
LUIGI_CLR   = (  0, 200,   0)   # green
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)

# ── Server connection ─────────────────────────────────────────────────────────
SERVER_IP = "localhost"
PORT = 5555
HANDSHAKE_TIMEOUT = 5.0  # seconds to wait for the initial server handshake


class Player:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.speed = 5

    # ---------- physics ----------

    def apply_gravity(self):
        if not self.on_ground:
            self.vel_y += GRAVITY

        self.y += self.vel_y

        # Simple ground collision
        if self.y + PLAYER_H >= GROUND_Y:
            self.y = GROUND_Y - PLAYER_H
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    # ---------- input ----------

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        self.x += self.vel_x
        # Keep player within horizontal window bounds
        self.x = max(0, min(WIDTH - PLAYER_W, self.x))

    # ---------- rendering ----------

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), PLAYER_W, PLAYER_H))
        # Simple "eyes"
        eye_y = int(self.y) + 10
        pygame.draw.circle(surface, WHITE, (int(self.x) + 10, eye_y), 5)
        pygame.draw.circle(surface, WHITE, (int(self.x) + 30, eye_y), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x) + 11, eye_y), 2)
        pygame.draw.circle(surface, BLACK, (int(self.x) + 31, eye_y), 2)


def draw_background(surface):
    surface.fill(SKY_BLUE)
    # Ground strip
    pygame.draw.rect(surface, GROUND_CLR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # Decorative ground line
    pygame.draw.line(surface, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)


def draw_labels(surface, font, player_index):
    my_name    = "Mario" if player_index == 0 else "Luigi"
    other_name = "Luigi" if player_index == 0 else "Mario"
    my_color    = MARIO_CLR if player_index == 0 else LUIGI_CLR
    other_color = LUIGI_CLR if player_index == 0 else MARIO_CLR
    surface.blit(font.render(f"{my_name} (you)",    True, my_color),    (10, 10))
    surface.blit(font.render(f"{other_name} (other)", True, other_color), (10, 35))


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mario & Luigi Multiplayer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # ── Connect to server ────────────────────────────────────────────────────
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to server at {SERVER_IP}:{PORT}. "
              "Make sure server.py is running first.")
        pygame.quit()
        sys.exit(1)

    client.settimeout(HANDSHAKE_TIMEOUT)

    # Receive "player_index,x,y" so we know our identity and start position
    try:
        start_data = client.recv(2048).decode("utf-8").split(",")
        if len(start_data) != 3:
            raise ValueError(f"Unexpected handshake format: {start_data}")
        player_index, start_x, start_y = int(start_data[0]), int(start_data[1]), int(start_data[2])
    except Exception as e:
        print(f"Failed to receive initial position: {e}")
        client.close()
        pygame.quit()
        sys.exit(1)

    client.settimeout(None)   # back to blocking

    my_color    = MARIO_CLR if player_index == 0 else LUIGI_CLR
    other_color = LUIGI_CLR if player_index == 0 else MARIO_CLR

    # Player 1 = this client.  Player 2 = remote opponent.
    p1 = Player(start_x, start_y, my_color)
    p2 = Player(0, GROUND_Y - PLAYER_H, other_color)

    run = True
    while run:
        clock.tick(FPS)

        # ── Event handling ───────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        # ── Physics & input for local player ────────────────────────────────
        p1.handle_input()
        p1.apply_gravity()

        # ── Network: send our position, receive opponent's ───────────────────
        try:
            msg = f"{int(p1.x)},{int(p1.y)}"
            client.sendall(msg.encode("utf-8"))

            reply = client.recv(2048).decode("utf-8").split(",")
            if len(reply) == 2:
                try:
                    p2.x = int(reply[0])
                    p2.y = int(reply[1])
                except ValueError:
                    pass  # keep last known position on bad data
        except Exception as e:
            print(f"Network error: {e}")
            run = False
            break

        # ── Rendering ────────────────────────────────────────────────────────
        draw_background(win)
        p1.draw(win)
        p2.draw(win)
        draw_labels(win, font, player_index)
        pygame.display.update()

    client.close()
    pygame.quit()


if __name__ == "__main__":
    main()
