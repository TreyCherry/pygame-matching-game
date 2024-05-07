import pygame
import random
import os
from pygame import display, event, image, transform

# Initialize Pygame
pygame.init()

# Constants
# Either add images to this path, or change this path to where you want your images
IMAGE_PATH = f'images'
# The colors I use in the program. If you want to change them, feel free.
TEXT_COLOR = (255, 255, 255)
CARD_BACK = (0, 0, 0)
CARD_BORDER = (255, 255, 255)
SIDEBAR_COLOR = (150, 0, 200)
BUTTON_COLOR = (0, 255, 0)
BUTTON_TEXT = (0, 0, 0)
BACKGROUND_COLOR = (200,200,200)

#These can be modified, as long as the math maths. 
GRID_COLS = 5  # Number of columns (horizontal cards)
GRID_ROWS = 4  # Number of rows (vertical cards)
CARD_SIZE = 180  # Fixed card size for consistent spacing
SIDEBAR_WIDTH = 200  # Width of the sidebar
SCREEN_WIDTH = CARD_SIZE * GRID_COLS + SIDEBAR_WIDTH
SCREEN_HEIGHT = CARD_SIZE * GRID_ROWS
FPS = 30
DELAY_MS = 1000  # Delay time in milliseconds (1 second). How long a set of cards stay face up.


# Set up the display
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption("Matching Game")

# Function for loading images
def load_random_images(path, num_pairs):
    images = []
    all_files = [file for file in os.listdir(path) if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    selected_files = random.sample(all_files, num_pairs)

    for file in selected_files:
        img = image.load(os.path.join(path, file))
        img = transform.scale(img, (CARD_SIZE, CARD_SIZE))
        images.append(img)
    return images

# Function to reset the game
def reset_game():
    global game_images, matched, revealed, first_click, second_click, last_click_time, num_turns, num_pairs
    num_pairs = (GRID_COLS * GRID_ROWS) // 2
    images = load_random_images(IMAGE_PATH, num_pairs=num_pairs)
    game_images = images * 2  # Each image needs to appear twice
    random.shuffle(game_images)
    matched = [False] * len(game_images)
    revealed = [False] * len(game_images)
    first_click = None
    second_click = None
    last_click_time = 0
    num_turns = 0

# Using reset function to initialize the game.
best_score = None
reset_game()

# Font
font = pygame.font.Font(None, 36)

# Clock
clock = pygame.time.Clock()

# Game Loop
running = True
while running:
    for e in event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN and not second_click:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if the reset button was clicked
            if SCREEN_WIDTH - SIDEBAR_WIDTH <= mouse_x <= SCREEN_WIDTH and 90 <= mouse_y <= 130:
                reset_game()
                continue

            #if the button wasn't clicked, check if a card needs flipping
            index_x = mouse_x // CARD_SIZE
            index_y = mouse_y // CARD_SIZE

            if index_x < GRID_COLS and index_y < GRID_ROWS:
                index = index_x + index_y * GRID_COLS
                if index < num_pairs * 2: # This is for the edge case where the corner is not occupied due to an odd number.
                    if not revealed[index] and not matched[index]:
                        revealed[index] = True
                        if first_click is None:
                            first_click = index
                        else:
                            second_click = index
                            last_click_time = pygame.time.get_ticks()
                            num_turns += 1

    # Check if it's time to hide unmatched pairs
    if second_click is not None:
        current_time = pygame.time.get_ticks()
        if current_time - last_click_time >= DELAY_MS:
            if game_images[first_click] == game_images[second_click]:
                matched[first_click] = True
                matched[second_click] = True
            else:
                revealed[first_click] = False
                revealed[second_click] = False
            first_click = None
            second_click = None

    # Check if the game is over and update the best score
    if all(matched):
        if best_score is None or num_turns < best_score:
            best_score = num_turns

    # Draw everything
    screen.fill(BACKGROUND_COLOR)
    for i in range(len(game_images)):
        x = (i % GRID_COLS) * CARD_SIZE
        y = (i // GRID_COLS) * CARD_SIZE
        if revealed[i] or matched[i]:
            screen.blit(game_images[i], (x, y))
        else:
            pygame.draw.rect(screen, CARD_BACK, (x, y, CARD_SIZE, CARD_SIZE))
            pygame.draw.rect(screen, CARD_BORDER, (x, y, CARD_SIZE, CARD_SIZE), 3)

    # Draw sidebar
    sidebar_x = SCREEN_WIDTH - SIDEBAR_WIDTH
    pygame.draw.rect(screen, SIDEBAR_COLOR, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
    turns_text = font.render(f"Turns: {num_turns}", True, TEXT_COLOR)
    screen.blit(turns_text, (sidebar_x + 10, 10))

    if best_score is not None:
        best_text = font.render(f"Best: {best_score}", True, TEXT_COLOR)
        screen.blit(best_text, (sidebar_x + 10, 50))

    # Draw reset button
    pygame.draw.rect(screen, BUTTON_COLOR, (sidebar_x + 10, 90, 180, 40))
    reset_text = font.render("Reset Game", True, BUTTON_TEXT)
    screen.blit(reset_text, (sidebar_x + 30, 95))

    display.flip()
    clock.tick(FPS)

pygame.quit()