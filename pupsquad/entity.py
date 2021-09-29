"""All entities in the game, i.e. the player, enemies and collectibles."""
import abc

import numpy as np
import pygame

from pupsquad.constant import GRAVITY
from pupsquad.constant import METERS
from pupsquad.constant import ROOT


class Character(pygame.sprite.Sprite, abc.ABC):
    """Abstract base class for characters."""

    def __init__(self, mass, position):
        super().__init__()

        # Initial entity state.
        self.mass = mass
        self.position = position
        self.velocity = np.array([0.*METERS, 0.*METERS])
        self.force = np.array([0., 0.])
        self.jumping = False

        # Entity sprite.
        self.image = pygame.Surface((1*METERS, 1*METERS))
        self.image.fill(pygame.Color("red"))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.position

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
        self.rect.midbottom = self.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Character):
    """The player character."""

    def __init__(self, position):
        # General entity settings.
        mass = 35.
        super().__init__(mass, position)
        # Player-specific settings.
        self.run_speed = 4.*METERS
        self.jump_height = 1.5*METERS
        # Player model.
        self.model = CharacterModelContext(PlayerIdleRight())

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

    def update(self, time_delta, decor):
        super().update(time_delta, decor)
        # Update current image depending on movement.
        self.model.update(self)
        self.image = self.model.image
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.position

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


class CharacterModelContext:
    """The character model context class."""

    _model = None
    """The current model of the character."""

    def __init__(self, model):
        self.transition_to(model)

    @property
    def image(self):
        return self._model.image

    def transition_to(self, model):
        """Transition to another model."""
        self._model = model
        self._model.context = self

    def update(self, *args, **kwargs):
        self._model.update(*args, **kwargs)


class CharacterModel(abc.ABC):
    """Abstract base class for character models."""

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
    def update(self, character):
        self.counter = (self.counter+1) % self.delay
        if self.counter == 0:
            self.index = (self.index+1) % len(self.images)


class PlayerIdleRight(CharacterModel):
    """Player idle, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/idle/1.png",
            "assets/player/idle/2.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallRight())
        elif character.velocity[1] > 0:
            self.context.transition_to(PlayerJumpRight())
        elif character.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif character.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())


class PlayerIdleLeft(CharacterModel):
    """Player idle, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/idle/1.png",
            "assets/player/idle/2.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallLeft())
        elif character.velocity[1] > 0:
            self.context.transition_to(PlayerJumpLeft())
        elif character.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif character.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())


class PlayerRunRight(CharacterModel):
    """Player running, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/run/1.png",
            "assets/player/run/2.png",
            "assets/player/run/3.png",
            "assets/player/run/4.png",
            "assets/player/run/5.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 5
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallRight())
        elif character.velocity[1] > 0:
            self.context.transition_to(PlayerJumpRight())
        elif character.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif character.velocity[0] == 0:
            self.context.transition_to(PlayerIdleRight())


class PlayerRunLeft(CharacterModel):
    """Player running, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/run/1.png",
            "assets/player/run/2.png",
            "assets/player/run/3.png",
            "assets/player/run/4.png",
            "assets/player/run/5.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 5
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallLeft())
        elif character.velocity[1] > 0:
            self.context.transition_to(PlayerJumpLeft())
        elif character.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())
        elif character.velocity[0] == 0:
            self.context.transition_to(PlayerIdleLeft())


class PlayerJumpRight(CharacterModel):
    """Player jumping, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/jump/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < 0.:
            self.context.transition_to(PlayerFallRight())
        elif character.velocity[0] < 0.:
            self.context.transition_to(PlayerJumpLeft())


class PlayerJumpLeft(CharacterModel):
    """Player jumping, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/jump/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] < 0.:
            self.context.transition_to(PlayerFallLeft())
        elif character.velocity[0] > 0.:
            self.context.transition_to(PlayerJumpRight())


class PlayerFallRight(CharacterModel):
    """Player falling, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/fall/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] == 0:
            self.context.transition_to(PlayerIdleRight())
        elif character.velocity[0] < 0.:
            self.context.transition_to(PlayerFallLeft())


class PlayerFallLeft(CharacterModel):
    """Player falling, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/fall/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, character):
        super().update(character)
        if character.velocity[1] == 0:
            self.context.transition_to(PlayerIdleLeft())
        elif character.velocity[0] > 0.:
            self.context.transition_to(PlayerFallRight())
