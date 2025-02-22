import constants
import pygame


def generate_lanes() -> list[tuple[int, int]]:
  # Calculate the actual width is used for point distribution
  usable_width = constants.WIDTH - (2 * constants.MARGIN_X)

  # Calculate the spacing between points
  spacing = usable_width / (constants.NUM_LANES - 1)

  # Add MARGIN to each x coordinate to offset from the left edge
  points = [(int(constants.MARGIN_X + (i * spacing)),
             constants.HEIGHT - constants.MARGIN_Y)
            for i in range(constants.NUM_LANES)]

  return points
