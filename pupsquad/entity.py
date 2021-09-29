"""Base classes for all entities in the game, i.e. player, enemies and other."""
import abc

import numpy as np
import pygame

from pupsquad.constant import GRAVITY
from pupsquad.constant import METERS
from pupsquad.constant import ROOT


class Entity(pygame.sprite.Sprite, abc.ABC):
    """Base class for entities, i.e. characters and objects."""

    def __init__(self, position, initial_image_state):
        super().__init__()

        # Initial entity state.
        self.position = position

        # Entity image.
        self.image_context = EntityImageContext(initial_image_state)
        self.image = self.image_context.image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    @abc.abstractmethod
    def update(self, time_delta, decor):
        """Update the entity state."""
        # Update the entity image state.
        self.image_context.update(self)
        self.image = self.image_context.image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Character(Entity):
    """Base class for characters, i.e. the player and enemies."""

    def __init__(self, position, initial_image_state, mass):
        super().__init__(position, initial_image_state)

        # Initial entity state.
        self.mass = mass
        self.velocity = np.array([0.*METERS, 0.*METERS])
        self.force = np.array([0., 0.])
        self.jumping = False

    def update(self, time_delta, decor):
        """Update the character state."""
        # Calculate position delta.
        acceleration = self.force/self.mass - [0., GRAVITY]
        self.velocity += acceleration*time_delta
        position_delta = np.round(self.velocity*time_delta)
        position_delta *= np.array([1, -1])
        # Check for collision with impassable decor.
        for tile in decor.tiles:
            if tile.passable:
                continue
            if tile.rect.colliderect(self.rect.move(position_delta[0], 0.)):
                if position_delta[0] >= 0:
                    position_delta[0] = tile.rect.left - self.rect.right
                elif position_delta[0] < 0:
                    position_delta[0] = tile.rect.right - self.rect.left
            if tile.rect.colliderect(self.rect.move(0., position_delta[1])):
                if position_delta[1] >= 0:
                    position_delta[1] = tile.rect.top - self.rect.bottom
                    self.jumping = False
                elif position_delta[1] < 0:
                    position_delta[1] = tile.rect.bottom - self.rect.top
                self.velocity[1] = 0.
        # Update the position.
        self.position += position_delta
        self.rect.center = self.position
        # Update the character image state.
        super().update(time_delta, decor)


class EntityImageContext:
    """The entity image context class."""

    _state = None
    """The current entity image state."""

    def __init__(self, state):
        self.transition_to(state)

    @property
    def image(self):
        return self._state.image

    def transition_to(self, state):
        """Transition to another image state."""
        self._state = state
        self._state.context = self

    def update(self, entity):
        self._state.update(entity)


class EntityImageState(abc.ABC):
    """Abstract base class for entity image states."""

    def __init__(self, image_fps, width, height, flip, delay):
        self.images = []
        for fp in image_fps:
            width = int(width)
            height = int(height)
            image = pygame.image.load(ROOT/fp).convert_alpha()
            image = pygame.transform.scale(image, (width, height))
            image = pygame.transform.flip(image, flip, False)
            self.images.append(image)
        self.delay = delay
        self.counter = 0
        self.index = 0

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @property
    def image(self):
        return self.images[self.index]

    @abc.abstractmethod
    def update(self, entity):
        self.counter = (self.counter+1) % self.delay
        if self.counter == 0:
            self.index = (self.index+1) % len(self.images)
