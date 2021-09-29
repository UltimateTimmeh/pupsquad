"""Classes for level decor."""
import pygame

from pupsquad.constant import TILE_SIZE


class DecorTile(pygame.sprite.Sprite):
    """A single tile in the decor."""

    def __init__(self, kind, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x*TILE_SIZE, y*TILE_SIZE)
        if kind == 0:
            self.image.fill(pygame.Color("grey"))
            self.passable = True
        else:
            self.image.fill(pygame.Color("black"))
            self.passable = False


class Decor:
    """A collection of decor tiles, forming a level's decor."""

    def __init__(self, grid):
        self.tiles = pygame.sprite.Group()
        for row_index, row in enumerate(grid):
            for column_index, kind in enumerate(row):
                tile = DecorTile(kind, column_index, row_index)
                self.tiles.add(tile)

    def draw(self, screen):
        self.tiles.draw(screen)
