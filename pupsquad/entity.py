"""All entities in the game, i.e. the player, enemies and collectibles."""
import abc

import numpy as np
import pygame

from pupsquad.constant import GRAVITY
from pupsquad.constant import METERS


class Character(pygame.sprite.Sprite, abc.ABC):
    """Abstract base class for characters."""

    def __init__(self, size, mass, position, velocity, force):
        super().__init__()

        # Initial entity state.
        self.size = size
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.force = force
        self.jumping = False

        # Entity sprite.
        self.image = pygame.Surface(self.size)
        self.image.fill(pygame.Color("red"))
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self, time_delta, decor):
        """Update the entity state."""
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

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Character):
    """The player character."""

    def __init__(self, position):
        # General entity settings.
        size = np.array([1.07*METERS, 0.74*METERS])
        mass = 35.
        velocity = np.array([0.*METERS, 0.*METERS])
        force = np.array([0., 0.])
        super().__init__(size, mass, position, velocity, force)
        # Player-specific settings.
        self.run_speed = 3.*METERS
        self.jump_height = 2*size[1]

    def handle_event(self, event):
        """Handle an event."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.jump()
            elif event.key == pygame.K_a:
                self.start_run_left()
            elif event.key == pygame.K_d:
                self.start_run_right()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.stop_run_left()
            elif event.key == pygame.K_d:
                self.stop_run_right()

    def jump(self):
        if self.jumping:
            return
        jump_velocity = (2*GRAVITY*self.jump_height)**0.5
        self.velocity[1] += jump_velocity
        self.jumping = True

    def start_run_left(self):
        self.velocity[0] -= self.run_speed

    def stop_run_left(self):
        self.velocity[0] += self.run_speed

    def start_run_right(self):
        self.velocity[0] += self.run_speed

    def stop_run_right(self):
        self.velocity[0] -= self.run_speed
