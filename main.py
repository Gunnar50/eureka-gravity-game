from operator import is_
import time
import constants
import sprites

import random

import pygame

import utils


class Game:

  def __init__(self):
    pygame.init()
    pygame.font.init()
    self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption(constants.TITLE)
    self.clock = pygame.time.Clock()
    self.debug = {}
    self.game_state = constants.GameState.IN_GAME

    self.background_image = pygame.image.load(
        'assets/Background01.png').convert_alpha()

    # Labels
    self.labels_background = pygame.Surface(
        (constants.WIDTH, constants.TOP_MARGIN))
    # self.start_game_label = sprites.UIElement(100, 100, 'PRESS ENTER TO START',
    #                                           constants.WHITE, 30)
    self.times_up_label = sprites.UIElement(100, 100, 'TIME IS UP!',
                                            constants.WHITE, 30)
    self.play_again_label = sprites.UIElement(100, 200,
                                              'PRESS ENTER TO PLAY AGAIN!',
                                              constants.WHITE, 30)
    self.score_label = sprites.UIElement(550, -10, 'SCORE 0000',
                                         constants.WHITE, 20)
    self.timer_label = sprites.UIElement(350, -10, '', constants.WHITE, 20)
    self.level_label = sprites.UIElement(100, -10, 'LEVEL 01', constants.WHITE,
                                         20)
    self.background_music = sprites.Audio('assets/background_music.mp3')
    self.background_music.play(loop=True)

  def new(self):
    self.game_state = constants.GameState.IN_GAME
    # Player
    self.lanes = utils.generate_lanes()
    self.player = sprites.Player()
    self.current_level = 1
    self.score = 0
    self.current_level_score = 0
    self.score_to_next_level = 100

    # Move cooldown timer
    self.timer = sprites.Timer()
    self.current_time = time.time()
    self.last_move_time = 0.0
    self.move_cooldown = 0.3

    # Fruits
    self.spawn_manager = sprites.SpawnManager()
    self.fruits = []

  def run(self):
    self.playing = True
    while self.playing:
      self.clock.tick(constants.FPS)
      self.events()
      self.update()
      self.draw()

  def update_level(self):
    if self.current_level_score >= self.score_to_next_level:
      self.current_level += 1
      self.current_level_score = 0
      self.level_label.update_text(f'LEVEL {self.current_level:02d}')
      # Reset timer
      self.timer.reset()

  def update(self):
    if self.game_state == constants.GameState.IN_GAME:
      # Check for times up
      if self.timer.is_finished():
        self.game_state = constants.GameState.GAME_OVER

      self.timer.update()
      self.timer_label.update_text(f'TIME {self.timer.get_time_string()}')
      self.player.update(self.lanes)

      self.current_time = time.time()
      # Reset cooldown timer
      if self.can_move():
        self.move_cooldown = 0.0
        self.player.can_move = True

      # Spawn new fruits
      if self.spawn_manager.should_spawn(self.current_level):
        image, is_apple, speed = self.spawn_manager.get_spawn_properties(
            self.current_level)
        lane = random.choice(self.lanes)[0]
        fruit = sprites.Fruit(
            x=lane,
            width=image.get_width(),
            height=image.get_height(),
            image=image,
            speed=speed,
            is_apple=is_apple,
        )
        self.fruits.append(fruit)

      # Check if collide and remove fruits
      fruit_to_remove = []
      for index, fruit in enumerate(self.fruits):
        fruit.update()
        if fruit.y <= constants.HEIGHT_THRESHOLD and self.player.collide(fruit):
          if fruit.is_apple:
            # If we get an apple, increase the move cooldown to 1s
            self.score += self.player.points
            self.current_level_score += self.player.points
            self.score_label.update_text(f'SCORE {self.score:04d}')
            self.update_level()
          else:
            # Otherwise, wrong fruit increase the move cooldown to 2s
            self.move_cooldown = 2.0
            self.player.can_move = False
          fruit_to_remove.append(index)

        # Remove fruits that are out of bounds with a margin
        elif fruit.y > constants.HEIGHT + constants.MARGIN_Y:
          fruit_to_remove.append(index)

      # Remove fruits from the fruits list
      for index in fruit_to_remove:
        self.fruits.pop(index)

  def draw(self):
    self.labels_background.fill(constants.BLACK)
    self.screen.blit(self.background_image, (0, constants.TOP_MARGIN))

    # Main menu
    if self.game_state == constants.GameState.MAIN_MENU:
      self.start_game_label.draw(self.screen)

    # In game
    elif self.game_state == constants.GameState.IN_GAME:
      self.player.draw(self.screen)

      for fruit in self.fruits:
        fruit.draw(self.screen)

      # Place the text labels on the labels_background surface
      # After the fruits have been drawn
      self.score_label.draw(self.labels_background)
      self.timer_label.draw(self.labels_background)
      self.level_label.draw(self.labels_background)
      self.screen.blit(self.labels_background, (0, 0))

    # Game over
    elif self.game_state == constants.GameState.GAME_OVER:
      self.times_up_label.draw(self.screen)

    if constants.DEBUG:
      self.debug['game_state'] = self.game_state
      self.debug['playing'] = self.playing
      utils.draw_info(self.debug, self.screen)
      pygame.draw.line(self.screen, constants.WHITE,
                       (0, constants.HEIGHT_THRESHOLD),
                       (constants.WIDTH, constants.HEIGHT_THRESHOLD))

    pygame.display.flip()

  def can_move(self) -> bool:
    return self.current_time - self.last_move_time >= self.move_cooldown

  def events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit(0)
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pygame.quit()
          quit(0)

        # Main menu
        if self.game_state == constants.GameState.MAIN_MENU:
          if event.key == pygame.K_RETURN:
            self.game_state = constants.GameState.IN_GAME

        # In game
        elif self.game_state == constants.GameState.IN_GAME:
          if self.can_move():
            if event.key == pygame.K_LEFT:
              self.player.move_left()
            elif event.key == pygame.K_RIGHT:
              self.player.move_right()
            self.last_move_time = self.current_time

          elif event.key == pygame.K_RETURN:
            self.game_state = constants.GameState.GAME_OVER

        # Game over
        elif self.game_state == constants.GameState.GAME_OVER:
          if event.key == pygame.K_RETURN:
            self.playing = False


if __name__ == '__main__':
  game = Game()
  while True:
    game.new()
    game.run()
