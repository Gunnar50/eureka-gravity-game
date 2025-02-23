import os
import random
import time
from typing import Optional
import pygame
import constants
import utils


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

  def __init__(self, lanes):
    self.lanes = lanes

    # APPLE SPAWNS
    self.apple_next_delay = random.uniform(1, 3)
    self.apple_last_spawn = time.time() - self.apple_next_delay
    self.apple_max_delay = 3.0
    self.apple_min_delay = 1.0
    # Never go lower than this for max delay
    self.apple_min_possible_delay = 0.3
    # How much to decrease per level
    self.apple_delay_decrease_rate = 0.6

    # OTHER FRUIT SPAWNS
    self.fruit_base_delay = 2.0
    self.fruit_delay_decrease_rate = 0.2
    self.fruit_min_delay = 0.5
    self.fruit_last_spawn = time.time()
    self.fruit_base_spawn_chance = 0.0
    self.fruit_chance_increase_per_level = 0.2
    self.fruit_max_spawn_chance = 0.8
    self.fruit_spawned_last = False

    self.fruits_speed_increase_per_level = 1.0

    self.occupied_lanes = []
    self.last_current_lane_clear = time.time()

    # Images
    self.apple_image = pygame.image.load('assets/Apple60px.png').convert_alpha()
    self.fruit_images = [
        pygame.image.load('assets/Banana80px.png').convert_alpha(),
        pygame.image.load('assets/Orange60px.png').convert_alpha(),
        pygame.image.load('assets/Grapes-60px.png').convert_alpha(),
        pygame.image.load('assets/Lemon60px.png').convert_alpha(),
        pygame.image.load('assets/Strawberry60px.png').convert_alpha(),
    ]

  def calculate_apple_delay(self, level: int) -> float:
    # Decrease max delay by delay_decrease_rate for each level
    current_max_delay = max(
        self.apple_max_delay - (self.apple_delay_decrease_rate * (level - 1)),
        self.apple_min_possible_delay)
    return random.uniform(self.apple_min_delay, current_max_delay)

  def get_safe_lane(self, occupied_lanes: list) -> Optional[int]:
    # Only store the x coordinate of the lanes
    available_lanes = [lane[0] for lane in self.lanes]
    if occupied_lanes:
      available_lanes = [
          lane for lane in available_lanes if lane not in occupied_lanes
      ]
    if available_lanes:
      return random.choice(available_lanes)

    return None

  def create_fruit(self, x, image, speed, is_apple) -> Fruit:
    return Fruit(
        x=x,
        width=image.get_width(),
        height=image.get_height(),
        image=image,
        speed=speed,
        is_apple=is_apple,
    )

  def spawn_fruits(self, level: int) -> list[Fruit]:
    current_time = time.time()
    new_fruits: list[Fruit] = []
    speed = min(
        constants.MAX_FRUIT_SPEED,
        constants.FRUIT_START_SPEED +
        (level * self.fruits_speed_increase_per_level),
    )

    # Clear occupied lanes every half second decreasing the rate by 0.05 per level
    clear_lane_delay = 0.5 - (0.05 * (level - 1))
    clear_lane_delay = max(clear_lane_delay, 0.1)
    if current_time - self.last_current_lane_clear >= clear_lane_delay:
      self.occupied_lanes.clear()
      self.last_current_lane_clear = current_time

    # Check for apple spawn
    if current_time - self.apple_last_spawn >= self.apple_next_delay:
      # Create apple
      lane = self.get_safe_lane(self.occupied_lanes)
      if lane is not None:
        self.occupied_lanes.append(lane)

        apple = self.create_fruit(x=lane,
                                  image=self.apple_image,
                                  speed=speed,
                                  is_apple=True)
        new_fruits.append(apple)

      # Reset apple spawn timer and generate new delay
      self.apple_last_spawn = current_time
      self.apple_next_delay = self.calculate_apple_delay(level)

    # Check for other fruit spawn
    # Calulate spawn delay, starting at 2.0s and decreasing by 0.2s per level
    current_delay_other_fruits = self.fruit_base_delay - (
        self.fruit_delay_decrease_rate * (level - 1))
    current_delay_other_fruits = max(current_delay_other_fruits, 0.3)
    if current_time - self.fruit_last_spawn >= current_delay_other_fruits:
      # Calculate spawn chance
      # Starting at 0% and goes up to 80% chance
      spawn_chance = self.fruit_base_spawn_chance + (
          self.fruit_chance_increase_per_level * (level - 1))
      spawn_chance = min(spawn_chance, self.fruit_max_spawn_chance)
      if random.random() < spawn_chance or (not self.fruit_spawned_last and
                                            level > 3):
        # Select random fruit image
        fruit_image = random.choice(self.fruit_images)

        # Get safe lane (different from apple if apple was spawned)
        lane = self.get_safe_lane(self.occupied_lanes)
        if lane is not None:
          self.occupied_lanes.append(lane)

          fruit = self.create_fruit(x=lane,
                                    image=fruit_image,
                                    speed=speed,
                                    is_apple=False)
          new_fruits.append(fruit)
          self.fruit_spawned_last = True
      else:
        self.fruit_spawned_last = False

      # Reset other fruit spawn timer
      self.fruit_last_spawn = current_time

      # Add some debugging info
      utils.debug_info['spawn_chance'] = spawn_chance if spawn_chance else 0
    utils.debug_info['current_delay_other_fruits'] = current_delay_other_fruits

    return new_fruits


class Audio:

  def __init__(self, file_path: str):
    pygame.mixer.init()
    self.audio = pygame.mixer.Sound(file_path)

  def play(self, loop=False):
    self.audio.play(loops=-1 if loop else 0)

  def stop(self):
    self.audio.stop()

  def set_volume(self, volume):
    self.audio.set_volume(volume)
