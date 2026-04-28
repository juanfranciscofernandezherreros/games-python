import pygame
import sys
import os

# --- Configuration & Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650
TILE_SIZE = 40  # size of ground blocks
FPS = 60

# Colors (as seen in the image)
SKY_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
TEXT_COLOR = WHITE

# Font Setup (uses a pixel font for authenticity)
# You need a font file like 'PressStart2P.ttf' in the same folder.
# If you don't have it, Pygame will use the default system pixel font.
pygame.font.init()
try:
    pixel_font = pygame.font.Font('PressStart2P.ttf', 24)
    label_font = pygame.font.Font('PressStart2P.ttf', 16)
except FileNotFoundError:
    # Use system fallback if asset is missing, but with a similar size
    pixel_font = pygame.font.SysFont('Arial_Pixed', 24)
    label_font = pygame.font.SysFont('Arial_Pixed', 16)
    print("Warning: Pixel font not found, using system fallback. Text will not match the image exactly.")

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Player 1 (Mario)")  # Set the specific window title
clock = pygame.time.Clock()

# --- Asset Loading (Pixel Art Simulation) ---
# For a runnable script, we use color blocks as placeholders.
# If you have actual assets, replace these with pygame.image.load().
def load_image(filename, scale_to_tile=False):
    """Loads an image or returns a color block placeholder if not found."""
    full_path = os.path.join('assets', filename)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if scale_to_tile:
            return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image
    except FileNotFoundError:
        print(f"Asset not found: {full_path}. Using placeholder.")
        # Placeholders
        if 'brick' in filename or 'ground' in filename:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((165, 42, 42))  # Brick Red
            return surf
        elif '?' in filename:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((255, 215, 0))  # Gold
            return surf
        elif 'stone' in filename:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((128, 128, 128))  # Stone Grey
            return surf
        elif 'cloud' in filename:
            surf = pygame.Surface((100, 50))
            surf.fill(WHITE)
            return surf
        elif 'pipe' in filename:
            surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2))
            surf.fill((0, 128, 0))  # Pipe Green
            return surf
        elif 'mario' in filename:
            surf = pygame.Surface((32, 48))
            surf.fill((255, 0, 0))  # Red Mario
            return surf
        elif 'luigi' in filename:
            surf = pygame.Surface((32, 48))
            surf.fill((0, 255, 0))  # Green Luigi
            return surf
        else:
            return pygame.Surface((10, 10))  # Small black box for other missing assets

# Load or create placeholder assets
# The image shows very specific sprites and block types.
# You need a proper file structure with 'assets/' to use real images.
mario_sprite = load_image('mario_walk.png')
luigi_sprite = load_image('luigi_stand.png')
brick_block_img = load_image('brick_block.png', scale_to_tile=True)
question_block_img = load_image('question_block.png', scale_to_tile=True)
stone_block_img = load_image('stone_block.png', scale_to_tile=True)
ground_block_img = load_image('ground_brick.png', scale_to_tile=True)
cloud_img = load_image('cloud.png')
pipe_img = load_image('pipe.png')

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite, character_name, is_player1=False):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = character_name
        self.vel_x = 0
        self.vel_y = 0
        self.jump_force = -15
        self.gravity = 0.8
        self.on_ground = False
        self.is_player1 = is_player1

    def handle_input(self):
        self.vel_x = 0
        keys = pygame.key.get_pressed()
        # Single keyboard control scheme for simulation
        if self.is_player1:
            if keys[pygame.K_LEFT]: self.vel_x = -5
            if keys[pygame.K_RIGHT]: self.vel_x = 5
            if keys[pygame.K_UP] and self.on_ground: self.jump()
        else:
            # Control Luigi with WASD for two players on one keyboard
            if keys[pygame.K_a]: self.vel_x = -5
            if keys[pygame.K_d]: self.vel_x = 5
            if keys[pygame.K_w] and self.on_ground: self.jump()

    def jump(self):
        self.vel_y = self.jump_force
        self.on_ground = False

    def update(self, solid_group):
        self.handle_input()

        # Gravity
        self.vel_y += self.gravity
        if self.vel_y > 15: self.vel_y = 15  # Cap falling speed

        # Move horizontally and handle collisions
        self.rect.x += self.vel_x
        # For simplicity, no x-collisions are implemented in this snippet

        # Move vertically and handle collisions
        self.rect.y += self.vel_y
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, solid_group, False)
        for hit in hits:
            if self.vel_y > 0:  # Falling
                self.rect.bottom = hit.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:  # Jumping
                self.rect.top = hit.rect.bottom
                self.vel_y = 0


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image, is_solid=True):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.is_solid = is_solid


# --- Game State ---
player1_pos = [150, 400]
player2_pos = [400, 400]
score = "002345"
lives = "03"

# --- Sprite Groups & Objects ---
all_sprites = pygame.sprite.Group()
solid_sprites = pygame.sprite.Group()

# 1. Create Ground (matches the image's layout)
# The image shows two rows of ground bricks.
for y in range(SCREEN_HEIGHT - (TILE_SIZE * 2), SCREEN_HEIGHT, TILE_SIZE):
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        b = Block(x, y, ground_block_img)
        all_sprites.add(b)
        solid_sprites.add(b)

# 2. Create Floating Blocks (match the layout)
# Block types: brick, question, brick, question, brick
for i, x_offset in enumerate([-80, -40, 0, 40, 80]):
    x = SCREEN_WIDTH // 2 - (TILE_SIZE // 2) + x_offset
    y = SCREEN_HEIGHT - (TILE_SIZE * 2) - TILE_SIZE
    if i in [1, 3]:  # Question marks at index 1 and 3
        b = Block(x, y, question_block_img)
    else:
        b = Block(x, y, brick_block_img)
    all_sprites.add(b)
    solid_sprites.add(b)

# High floating blocks: brick, question, brick, stone
for i, x_offset in enumerate([-TILE_SIZE * 2, -TILE_SIZE, 0, TILE_SIZE]):
    x = SCREEN_WIDTH - (TILE_SIZE * 5) + x_offset
    y = 200  # Roughly the height in the image
    if i == 1:  # Question mark at index 1
        b = Block(x, y, question_block_img)
    elif i == 3:  # Stone block at index 3
        b = Block(x, y, stone_block_img)
    else:
        b = Block(x, y, brick_block_img)
    all_sprites.add(b)
    solid_sprites.add(b)

# Single low question block
b = Block(400, 200, question_block_img)
all_sprites.add(b)
solid_sprites.add(b)

# 3. Create Cloud Sprites
clouds = [(200, 100), (SCREEN_WIDTH // 2, 100), (SCREEN_WIDTH - 200, 100)]
for cx, cy in clouds:
    b = Block(cx, cy, cloud_img, is_solid=False)
    all_sprites.add(b)

# 4. Create Pipe
pipe = Block(SCREEN_WIDTH - TILE_SIZE * 6, SCREEN_HEIGHT - (TILE_SIZE * 4), pipe_img)
all_sprites.add(pipe)
solid_sprites.add(pipe)

# 5. Create Players
# Set is_player1 to True for Mario to control him with arrow keys.
player1 = Player(player1_pos[0], player1_pos[1], mario_sprite, "Mario", is_player1=True)
# Luigi is controlled with WASD.
player2 = Player(player2_pos[0], player2_pos[1], luigi_sprite, "Luigi", is_player1=False)
all_sprites.add(player1, player2)

# Create text labels to be attached to players
p1_label = label_font.render("P1: Mario", True, TEXT_COLOR)
p2_label = label_font.render("P2: Luigi", True, TEXT_COLOR)

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 2. Update Game State
    player1.update(solid_sprites)
    player2.update(solid_sprites)

    # Dynamic positions in HUD
    player1_pos = [player1.rect.x, player1.rect.y]
    player2_pos = [player2.rect.x, player2.rect.y]

    # 3. Render / Draw
    screen.fill(SKY_BLUE)  # Background color

    # Draw all environment sprites first (clouds are back-to-front)
    all_sprites.draw(screen)

    # Draw player labels right above their sprites
    screen.blit(p1_label, (player1.rect.centerx - p1_label.get_width() // 2, player1.rect.top - 20))
    screen.blit(p2_label, (player2.rect.centerx - p2_label.get_width() // 2, player2.rect.top - 20))

    # Draw HUD (exact text and positions from image)
    screen.blit(pixel_font.render(f"SCORE: {score}", True, TEXT_COLOR), (20, 20))
    screen.blit(pixel_font.render(f"LIVES: {lives}", True, TEXT_COLOR), (20, 60))
    screen.blit(pixel_font.render(f"P1 POS: [{player1_pos[0]}, {player1_pos[1]}]", True, TEXT_COLOR), (20, 100))
    screen.blit(pixel_font.render(f"P2 POS: [{player2_pos[0]}, {player2_pos[1]}]", True, TEXT_COLOR), (20, 140))

    pygame.display.flip()
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
