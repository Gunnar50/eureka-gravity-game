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
    self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption(constants.TITLE)
    self.clock = pygame.time.Clock()
    self.game_state = constants.GameState.IN_GAME
    self.level = 1

    # Labels
    self.start_game_label = sprites.UIElement(100, 100, 'PRESS ENTER TO START',
                                              constants.WHITE, 30)
    self.points_label = sprites.UIElement(100, 100, 'Points: 0',
                                          constants.WHITE, 30)
    self.game_over_label = sprites.UIElement(100, 100,
                                             'PRESS ENTER TO PLAY AGAIN',
                                             constants.WHITE, 30)
    self.timer_label = sprites.UIElement(200, 50, '', constants.WHITE, 30)

    # Player
    self.lanes = utils.generate_lanes()
    self.player = sprites.Player()
    self.points = 0

    # Move cooldown timer
    self.timer = sprites.Timer()
    self.current_time = time.time()
    self.last_move_time = 0.0
    self.move_cooldown = 0.3

    # Fruits
    self.fruits = [
        sprites.Fruit(
            x=self.lanes[random.randint(0,
                                        len(self.lanes) - 1)][0],
            colour=constants.RED,
            is_apple=True,
        ),
    ]

  def new(self):
    pass

  def reset_variables(self):
    pass

  def run(self):
    self.playing = True
    while self.playing:
      self.clock.tick(constants.FPS)
      self.events()
      self.update()
      self.draw()

  def update(self):
    self.timer.update()
    self.timer_label.update_text(f'{self.timer.get_time_string()}')
    self.player.update(self.lanes)

    self.current_time = time.time()
    # Reset cooldown timer
    if self.can_move():
      self.move_cooldown = 0.0

    # Spawn new fruits
    if random.random() < 0.01:
      # TODO: Find better way to spawn fruits
      if random.random() < 0.7:
        colour = constants.RED
        is_apple = True
      else:
        colour = constants.COLOURS[random.randint(1,
                                                  len(constants.COLOURS) - 1)]
        is_apple = False
      lane = self.lanes[random.randint(0, len(self.lanes) - 1)][0]
      fruit = sprites.Fruit(
          x=lane,
          colour=colour,
          is_apple=is_apple,
      )
      self.fruits.append(fruit)

    # Remove fruits
    fruit_to_remove = []
    for index, fruit in enumerate(self.fruits):
      fruit.update()
      if self.player.collide(fruit):
        if fruit.is_apple:
          # If we get an apple, increase the move cooldown to 1s
          self.points += 1
          self.points_label.update_text(f'Points: {self.points}')
        else:
          # Otherwise, wrong fruit increase the move cooldown to 2s
          self.move_cooldown = 2.0
        fruit_to_remove.append(index)

      # Remove fruits that are out of bounds with a margin
      elif fruit.y > constants.HEIGHT + constants.MARGIN_Y:
        fruit_to_remove.append(index)

    for index in fruit_to_remove:
      self.fruits.pop(index)

  def draw(self):
    self.screen.fill(constants.BGCOLOUR)

    # Main menu
    if self.game_state == constants.GameState.MAIN_MENU:
      self.start_game_label.draw(self.screen)

    # In game
    elif self.game_state == constants.GameState.IN_GAME:
      self.points_label.draw(self.screen)
      self.player.draw(self.screen)

      for fruit in self.fruits:
        fruit.draw(self.screen)

      self.timer_label.draw(self.screen)

    # Game over
    elif self.game_state == constants.GameState.GAME_OVER:
      self.game_over_label.draw(self.screen)

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
            self.game_state = constants.GameState.MAIN_MENU


if __name__ == '__main__':
  game = Game()
  while True:
    game.new()
    game.run()
