#I will dynamically (automatically) load all of the sprite sheets & images, without the need for manually specifying each file name.  
import os 
import random 
import math 
import pygame 
from os import listdir
from os.path import isfile, join

# Initialize pygame module
pygame.init()

# Used to set the title or caption that appears at the top of the game window.
pygame.display.set_caption("Adventure")

# Define global variables 
WIDTH, HEIGHT = 900, 700
# Frames displayer per second
FPS = 60  
# Player velocity - speed at which the player moves around the screen.
PLAYER_VEL = 5

# Set up a pygame window 
window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    # Create a flipped version of the sprite by flipping it horizontally. 
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Construct the path to the sprite sheets directory
    path = join("assets", dir1, dir2)
    # Load every single file in that directory 
    images = [f for f in listdir(path) if isfile(join(path, f))]

    # Empty dictionary which will be used to store the loaded sprite sheets.
    all_sprites = {}

    for image in images:
        # The loaded image is converted to a format that supports transparency.
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            # Create a new surface for the individual sprite
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            # Define the rectangle representing the current sprite's position and dimensions
            rect = pygame.Rect(i * width, 0, width, height)
            # Copy the current sprite from the sprite sheet to the new surface
            # Essentially drawing the frame from the wanted sprite sheet.
            surface.blit(sprite_sheet, (0, 0), rect)
            # Surface -> double the size. 
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            # If you want a multi directional animation. 
            # Add the sprites to the `all_sprites` dictionary with different keys for right and left directions.
            # The sprite sheet image name is used as a base, and "_right" and "_left" are appended to distinguish the directions(strices facing).
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        
        else:
            # If you don't want multi-directional animation.
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


# This function is used to retrieve a block of a specified size from a larger image.
# The block represents a portion of the image and will be returned as a scaled surface.
def get_block(size):

    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    
    # The position (96, 0) indicates the starting coordinates within the image where the block is located
    rect = pygame.Rect(96, 0 , size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

# Using sprite -> handle collisions 
class Player(pygame.sprite.Sprite):
    # Color of the player
    COLOR = (255, 0, 0)
    GRAVITY = 1
    # You want multi directional animantion (left and right), so pass True.
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        # Player's velocity in the horizontal direction
        self.x_vel = 0  
        # Player's velocity in the vertical direction
        self.y_vel = 0
        # Collision mask (currently not assigned)
        self.mask = None
        # Direction the player is facing (initially set to "left")
        self.direction = "left"
        self.animation_count = 0
        self.gravity_fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        # Changing velocity to go upwards and allow gravity to take player downwards
        self.y_vel = -self.GRAVITY * 8
        # This ensures that the player's jump animation starts from the beginning
        self.animation_count = 0

        # Increment the jump count by 1
        # This keeps track of the number of jumps performed by the player
        self.jump_count += 1

        # If this is the first jump, reset the gravity fall count to 0
        if self.jump_count == 1:
            self.gravity_fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move_left(self, vel):
        self.x_vel = -vel
        # Check if player is already facing left
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        # Check if player is already facing right
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Its called every frame (one iteration of the while loop)
    # Move the player by updating its position based on the current velocity
    def loop(self, fps): 
        # Update vertical velocity based on gravity
        self.y_vel += min(1, (self.gravity_fall_count / fps) * self.GRAVITY)
        # Update vertical velocity based on gravity
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.gravity_fall_count += 1
        self.update_sprite()

    def landed(self):
        # Stop adding gravity 
        self.gravity_fall_count = 0 
        self.y_vel = 0
        self.jump_count = 0
        
    def hit_head(self):
        self.count = 0
        # If player hits head then it will bounce off the block and go downwards
        self.y_vel *= -1

    def update_sprite(self):
        # IDLE is default spride sheet
        sprite_sheet = "idle"
        
        if self.hit:
            sprite_sheet = "hit"

        # Moving up
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"

        # Moving down
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"

        # If the horizontal velocity is not zero (indicating movement), switch to the "run" sprite sheet
        elif self.x_vel != 0:
            sprite_sheet = "run"

        # Create the name of the sprite sheet to be used based on the animation and direction.
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        # Get the list of sprites corresponding to the specified sprite sheet name.
        sprites = self.SPRITES[sprite_sheet_name]

        # Calculate the index of the current sprite based on the animation count and delay.
        # Animation delay: Every 3 frames, we show a different sprite in the animation (ex. using "running left" or "idle").
        # Dynamic sprite animation allows for a series of images (sprites) to be displayed in succession, creating the perception of motion.
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        
        # Update the current sprite being displayed & advance the animation count for the next frame.
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update()
    
    def update(self):
        # Adjust the width and height of the rectangle based on the sprite. 
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # Create or update the collision mask based on the transparency of the sprite image.
        self.mask = pygame.mask.from_surface(self.sprite)

    # Draw the player 
    def draw(self, win, offset_x):
        # Draw sprite image onto game window at specified position.
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        # Create a rectangle object to represent the object's position and size
        self.rect = pygame.Rect(x, y, width, height)
        
        # Create a surface (image) for the object with the specified width and height
        # The pygame.SRCALPHA flag indicates that the surface supports transparency
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        # Draw the object's image on the window at the current position specified by the rectangle.
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# This allows the block object to be displayed on the game screen & enables collision detection with other objects in the game.
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        # Load the sprite sheets for the fire animation and store them in the `fire` attribute.
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)

        # Set the initial image to the first frame of the "off" animation.
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)

        # Initialize the animation count and set the initial animation name to "off"
        self.animation_count = 0
        self.animation_name = "off"

    # Set the animation name to "on" & "off"
    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        # Get the sprites for the current animation name
        sprites = self.fire[self.animation_name]
        # Calculate the index of the current sprite based on the animation count
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        
        # Update the current sprite being displayed & advance the animation count for the next frame.
        self.image = sprites[sprite_index]
        self.animation_count += 1

        # Adjust the width and height of the rectangle based on the image. 
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        # Create or update the collision mask based on the transparency of the image.
        self.mask = pygame.mask.from_surface(self.image)

        # Reset the animation count if it exceeds the number of frames in the current animation
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    # Load the image file from the specified path. 
    image = pygame.image.load(join("assets", "Background", name))
    
    # Getting the Image Dimensions (rectangle object)
    _, _, width, height = image.get_rect()
    
    # Create an empty list to store tile positions.
    tiles = []

    # Calculate the number of tiles needed to fill the screen
    # by dividing the screen width and height by the tile width and height,
    # Adding 1 to account for any remaining partial tiles
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            # Gives position of where I need to place the tile. 
            pos = (i * width, j * height)
            # Add the position to the list of tiles
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    # Loop through every tile and draw the background image at that position to fill the screen.
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        # To check for collision between the player and the current object.
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                # Place player on top of the object that it collided with 
                # Players "feet" will be equal to the top of the object  
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom 
                player.hit_head()
            
            collided_objects.append(obj)
    
    return collided_objects


def collide(player, objects, dx):
    # Move the player horizontally
    player.move(dx, 0)
    player.update()
    collided_object = None

    # Check for collisions with each object.
    for obj in objects:
        # Check for collision between the player and the current object using pixel masks
        if pygame.sprite.collide_mask(player, obj):
            # Store the collided object
            collided_object = obj
            break

    # Reset the player's position to its original state
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    # This tells you all of the keys on the keyboard that are currently being pressed.
    keys = pygame.key.get_pressed()

    # Only move when holding down the key

    player.x_vel = 0
    # Check for collisions on the left and right sides of the player
    # (* 2) adds space between player and block
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    # Check if are able to move left/right based on the current position.
    # Check if the corresponding keys are pressed and there are no collisions.
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    # Check if player collided with fire, if yes then put hit 
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

# What we run to essentially start the game.
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Purple.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(150, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    game_over = False

    # -Width is how many blocks wanted for the left side, the other is for the right side
    # Height - block size means the blocks will be at the bottom
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
              for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    
    # Breaks floor into individual elements
    # objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
               # Block(block_size * 3, HEIGHT - block_size * 4, block_size), Block(block_size * 6, HEIGHT - block_size * 3, block_size) , fire]

    # Create a list to hold the blocks
    blocks = [Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
              Block(block_size * 3, HEIGHT - block_size * 3, block_size), Block(block_size * 3, HEIGHT - block_size * 5, block_size)]

    # Add new blocks to the blocks list (different way)
    blocks.append(Block(500, HEIGHT - block_size - 110, block_size))
    blocks.append(Block(500, HEIGHT - block_size - 205, block_size))
    blocks.append(Block(600, HEIGHT - block_size - 350, block_size))
    blocks.append(Block(695, HEIGHT - block_size - 350, block_size))
    blocks.append(Block(790, HEIGHT - block_size - 350, block_size))
    blocks.append(Block(885, HEIGHT - block_size - 350, block_size))
    blocks.append(Block(1100, HEIGHT - block_size - 190, block_size))
    blocks.append(Block(1250, HEIGHT - block_size - 190, block_size))
    blocks.append(Block(1400, HEIGHT - block_size - 400, block_size))
    blocks.append(Block(1495, HEIGHT - block_size - 400, block_size))
    blocks.append(Block(1600, HEIGHT - block_size - 500, block_size))

    # Extend the objects list with the blocks list
    # This will ensure that the new blocks are included in the objects list along with the existing blocks.
    objects = [*floor, *blocks, fire]


    offset_x = 0
    scroll_area_width = 200
    # Allows the game to run as long as run remains true.
    run = True
    while run:
        # Ensures that the while loop runs 60 times per sec.
        clock.tick(FPS)

        # EVENT HANDLING 
        for event in pygame.event.get():
            # To close/quit the game window, game loop should exit & the game should stop running.
            if event.type == pygame.QUIT:
                run = False
                break 
            # WHEN YOU RELEASE THE KEY
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        # loop is what actually moves the players
        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # Checks if the player is moving towards the right/left edge of the screen and if the player's position is close to the edge where scrolling should occur.
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            # Update the horizontal scroll offset by adding the player's horizontal velocity
            offset_x += player.x_vel

        # Check if the player falls off the last block
        if player.rect.y > HEIGHT:
            game_over = True

        if game_over:
            font = pygame.font.Font(None, 100)
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(game_over_text, text_rect)
            pygame.display.update()
            pygame.time.delay(7000)  # Delay for 7 seconds before quitting the game
            break


    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)