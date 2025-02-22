import random
import time
import pygame
import constants


class Sprite:

  def __init__(
      self,
      x: int = 0,
      y: int = 0,
      width: int = 50,
      height: int = 50,
      colour: tuple[int, int, int] = constants.WHITE,
  ):
    self.x, self.y = x, y
    self.width, self.height = width, height
    self.colour = colour

  def draw(self, screen: pygame.Surface):
    draw_x, draw_y = self.x - self.width // 2, self.y - self.height // 2
    pygame.draw.rect(screen, self.colour,
                     (draw_x, draw_y, self.width, self.height))

  def collide(self, other: "Sprite") -> bool:
    return (self.x < other.x + other.width and self.x + self.width > other.x and
            self.y < other.y + other.height and self.y + self.height > other.y)


class Player(Sprite):

  def __init__(self):
    Sprite.__init__(self)
    self.current_lane = 2

  def update(self, lanes: list[tuple[int, int]]):
    self.x, self.y = lanes[self.current_lane]

  def move_left(self):
    self.current_lane = max(self.current_lane - 1, 0)

  def move_right(self):
    self.current_lane = min(self.current_lane + 1, constants.NUM_LANES - 1)


class Fruit(Sprite):

  def __init__(self, x: int, colour, is_apple=False):
    self.is_apple = is_apple
    self.speed = 5
    self.width, self.height = 20, 20
    Sprite.__init__(
        self,
        x=x,
        y=-self.height,
        width=self.width,
        height=self.height,
        colour=colour,
    )

  def update(self):
    self.y += self.speed


class UIElement:

  def __init__(self, x, y, text, colour, font_size=40, alpha=255):
    self.x, self.y = x, y
    self.text = text
    self.colour = colour
    self.font_size = font_size
    self.alpha = alpha
    self.create_font()

  def create_font(self):
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

  def __init__(self, total_seconds: int = 120):
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
    minutes = self.remaining_seconds // 60
    seconds = self.remaining_seconds % 60
    # Format as MM:SS
    return f"{minutes:02d}:{seconds:02d}"

  def is_finished(self):
    return self.remaining_seconds <= 0


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

  def get_current_spawn_delay(self) -> float:
    # Decrease spawn delay as level increases
    # Each level makes spawning 10% faster
    current_delay = self.base_spawn_delay * (0.9**(self.level - 1))
    # Don't go faster than min_spawn_delay
    return max(current_delay, self.min_spawn_delay)

  def update_level(self):
    self.level += 1

  def should_spawn(self) -> bool:
    current_time = time.time()
    if current_time - self.last_spawn_time >= self.get_current_spawn_delay():
      self.last_spawn_time = current_time
      return True
    return False

  def get_spawn_properties(self):
    # Different spawn probabilities for different levels
    # Decrease apple probability as level increases
    apple_probability = 1.0 - (self.level * 0.05)
    # Don't go lower than 50% chance
    apple_probability = max(0.5, apple_probability)

    if random.random() < apple_probability:
      colour = constants.RED
      is_apple = True
    else:
      colour = constants.COLOURS[random.randint(0, len(constants.COLOURS) - 1)]
      is_apple = False

    return colour, is_apple
