import os
import random
import time
from typing import Optional
import pygame
import constants


class Sprite:

  def __init__(
      self,
      x: float = 0,
      y: float = 0,
      width: int = 0,
      height: int = 0,
      image: Optional[pygame.Surface] = None,
      colour: tuple[int, int, int] = constants.WHITE,
  ):
    self.x, self.y = x, y
    self.hitbox_x, self.hitbox_y = x, y
    self.width, self.height = width, height
    self.colour = colour
    self.image = image

  def draw(self, screen: pygame.Surface):
    draw_x, draw_y = (self.x - self.width // 2, self.y - self.height // 2)
    if self.image:
      screen.blit(self.image, (draw_x, draw_y))

    if constants.DEBUG:
      # Draw hitboxes for debugging
      pygame.draw.rect(screen,
                       self.colour,
                       (self.hitbox_x, self.hitbox_y, self.width, self.height),
                       width=2)

  def collide(self, other: "Sprite") -> bool:
    return (self.hitbox_x < other.hitbox_x + other.width and
            self.hitbox_x + self.width > other.hitbox_x and
            self.hitbox_y < other.hitbox_y + other.height and
            self.hitbox_y + self.height > other.hitbox_y)


class Player(Sprite):

  def __init__(self):
    self.newton_image = pygame.image.load('assets/Newton.png').convert_alpha()
    self.newton_ouch_image = pygame.image.load(
        'assets/Newton-Ouch.png').convert_alpha()
    Sprite.__init__(
        self,
        image=self.newton_image,
        width=self.newton_image.get_width(),
        height=self.newton_image.get_height(),
    )
    self.current_lane = 2
    self.points = 10
    self.can_move = True

  def update_image(self) -> None:
    if self.can_move:
      self.image = self.newton_image
    else:
      self.image = self.newton_ouch_image

    if self.image:
      self.width = self.image.get_width()
      self.height = self.image.get_height()

  def update_draw_position(self):
    self.hitbox_x, self.hitbox_y = (
        self.x - self.width // 2,
        (self.y + constants.PLAYER_HITBOX_OFFSET_Y) - self.height // 2)

  def update(self, lanes: list[tuple[int, int]]):
    self.x, self.y = lanes[self.current_lane]
    self.update_draw_position()
    self.update_image()

  def move_left(self):
    self.current_lane = max(self.current_lane - 1, 0)

  def move_right(self):
    self.current_lane = min(self.current_lane + 1, constants.NUM_LANES - 1)


class Fruit(Sprite):

  def __init__(self,
               x: int,
               image,
               width: int,
               height: int,
               speed,
               is_apple=False):
    self.is_apple = is_apple
    self.speed = speed
    self.width, self.height = width, height
    Sprite.__init__(
        self,
        x=x,
        y=-self.height,
        width=self.width,
        height=self.height,
        colour=constants.WHITE,
        image=image,
    )

  def update_draw_position(self):
    self.hitbox_x, self.hitbox_y = (self.x - self.width // 2,
                                    (self.y) - self.height // 2)

  def update(self):
    self.y += self.speed
    self.update_draw_position()


class UIElement:

  def __init__(self, x, y, text, colour, font_size=40, alpha=255):
    self.x, self.y = x, y
    self.text = text
    self.colour = colour
    self.font_size = font_size
    self.alpha = alpha
    self.create_font()

  def create_font(self):
    font_path = 'assets/Pixeled.ttf'
    try:
      font = pygame.font.Font(font_path, self.font_size)
    except pygame.error:
      print(
          f"Could not load font file {font_path}. Falling back to system font.")
      # Fallback to system font if custom font fails to load
      font = pygame.font.SysFont("Consolas", self.font_size)

    self.original_surf = font.render(self.text, True, self.colour)
    self.text_surf = self.original_surf.copy()
    # this surface is used to adjust the alpha of the text_surf
    self.alpha_surf = pygame.Surface(self.text_surf.get_size(), pygame.SRCALPHA)

  def draw(self, screen):
    self.text_surf = self.original_surf.copy(
    )  # dont modify the original text_surf
    self.alpha_surf.fill(
        (255, 255, 255,
         self.alpha))  # fill alpha_surf with colour to set its alpha value
    self.text_surf.blit(self.alpha_surf, (0, 0),
                        special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(self.text_surf, (self.x, self.y))

  def update_text(self, text: str) -> None:
    self.text = text
    self.create_font()

  def fade_out(self):
    self.alpha = max(self.alpha - 10, 0)  # reduce alpha each frame, up to 0
    self.text_surf = self.original_surf.copy(
    )  # dont modify the original text_surf
    self.alpha_surf.fill(
        (255, 255, 255,
         self.alpha))  # fill alpha_surf with colour to set its alpha value
    self.text_surf.blit(self.alpha_surf, (0, 0),
                        special_flags=pygame.BLEND_RGBA_MULT)

  def fade_in(self):
    self.alpha = min(self.alpha + 10, 255)  # reduce alpha each frame, up to 0
    self.text_surf = self.original_surf.copy(
    )  # dont modify the original text_surf
    self.alpha_surf.fill(
        (255, 255, 255,
         self.alpha))  # fill alpha_surf with colour to set its alpha value
    self.text_surf.blit(self.alpha_surf, (0, 0),
                        special_flags=pygame.BLEND_RGBA_MULT)


class Timer:

  def __init__(self, total_seconds: int = 30):
    self.total_seconds = total_seconds
    self.remaining_seconds = total_seconds
    self.last_tick = time.time()
    self.is_running = True

  def update(self):
    if self.is_running and self.remaining_seconds > 0:
      current_time = time.time()
      if current_time - self.last_tick >= 1:
        self.remaining_seconds -= 1
        self.last_tick = current_time

  def get_time_string(self):
    seconds = self.remaining_seconds % 60
    # Format as MM:SS
    return f'{seconds:02d}'

  def is_finished(self):
    return self.remaining_seconds <= 0

  def reset(self):
    self.remaining_seconds = self.total_seconds
    self.last_tick = time.time()


class SpawnManager:

  def __init__(self):
    self.level = 1
    self.last_spawn_time = time.time()
    # Start with 1 second between spawns
    self.base_spawn_delay = 2.0
    # Fastest spawn rate
    self.min_spawn_delay = 0.3
    self.last_level_up_time = time.time()

    self.level_duration = 20

    # Images
    self.apple_image = pygame.image.load('assets/Apple60px.png').convert_alpha()
    self.banana_image = pygame.image.load(
        'assets/Banana80px.png').convert_alpha()
    self.orange_image = pygame.image.load(
        'assets/Orange60px.png').convert_alpha()
    self.fruit_images = [self.banana_image, self.orange_image]

  def should_spawn(self, level: int) -> bool:
    # Decrease spawn delay as level increases
    # Each level makes spawning 5% faster
    current_delay = self.base_spawn_delay * (0.95**(level - 1))
    min_delay = max(current_delay, self.min_spawn_delay)
    current_time = time.time()
    if current_time - self.last_spawn_time >= min_delay:
      self.last_spawn_time = current_time
      return True
    return False

  def get_spawn_properties(self, level: int):
    # Different spawn probabilities for different levels
    # Decrease apple probability as level increases
    apple_probability = 1.10 - (level * 0.10)
    # Don't go lower than 40% chance
    apple_probability = max(0.4, apple_probability)
    # Fruit speed increase with each level
    fruit_speed = min(constants.MAX_FRUIT_SPEED,
                      constants.FRUIT_START_SPEED + (level * 0.5))

    if random.random() < apple_probability:
      image = self.apple_image
      is_apple = False
    else:
      image = random.choice(self.fruit_images)
      is_apple = False

    return image, is_apple, fruit_speed
