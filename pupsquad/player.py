"""Classes for the player."""
import pygame

import pupsquad.entity
from pupsquad.constant import GRAVITY
from pupsquad.constant import METERS


class Player(pupsquad.entity.Character):
    """The player character."""

    def __init__(self, position):
        # General entity settings.
        initial_image_state = PlayerIdleRight()
        mass = 35.
        super().__init__(position, initial_image_state, mass)
        # Player-specific settings.
        self.run_speed = 4.*METERS
        self.jump_height = 1.5*METERS

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


class PlayerIdleRight(pupsquad.entity.EntityImageState):
    """Image state for player idle, facing right."""

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

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallRight())
        elif entity.velocity[1] > 0:
            self.context.transition_to(PlayerJumpRight())
        elif entity.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif entity.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())


class PlayerIdleLeft(pupsquad.entity.EntityImageState):
    """Image state for player idle, facing left."""

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

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallLeft())
        elif entity.velocity[1] > 0:
            self.context.transition_to(PlayerJumpLeft())
        elif entity.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif entity.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())


class PlayerRunRight(pupsquad.entity.EntityImageState):
    """Image state for player running, facing right."""

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

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallRight())
        elif entity.velocity[1] > 0:
            self.context.transition_to(PlayerJumpRight())
        elif entity.velocity[0] < 0:
            self.context.transition_to(PlayerRunLeft())
        elif entity.velocity[0] == 0:
            self.context.transition_to(PlayerIdleRight())


class PlayerRunLeft(pupsquad.entity.EntityImageState):
    """Image state for player running, facing left."""

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

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < -0.5*METERS:
            self.context.transition_to(PlayerFallLeft())
        elif entity.velocity[1] > 0:
            self.context.transition_to(PlayerJumpLeft())
        elif entity.velocity[0] > 0:
            self.context.transition_to(PlayerRunRight())
        elif entity.velocity[0] == 0:
            self.context.transition_to(PlayerIdleLeft())


class PlayerJumpRight(pupsquad.entity.EntityImageState):
    """Image state for player jumping, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/jump/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < 0.:
            self.context.transition_to(PlayerFallRight())
        elif entity.velocity[0] < 0.:
            self.context.transition_to(PlayerJumpLeft())


class PlayerJumpLeft(pupsquad.entity.EntityImageState):
    """Image state for player jumping, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/jump/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] < 0.:
            self.context.transition_to(PlayerFallLeft())
        elif entity.velocity[0] > 0.:
            self.context.transition_to(PlayerJumpRight())


class PlayerFallRight(pupsquad.entity.EntityImageState):
    """Image state for player falling, facing right."""

    def __init__(self):
        image_fps = [
            "assets/player/fall/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = True
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] == 0:
            self.context.transition_to(PlayerIdleRight())
        elif entity.velocity[0] < 0.:
            self.context.transition_to(PlayerFallLeft())


class PlayerFallLeft(pupsquad.entity.EntityImageState):
    """Image state for player falling, facing left."""

    def __init__(self):
        image_fps = [
            "assets/player/fall/1.png",
        ]
        width = 1.15*METERS
        height = 0.74*METERS
        flip = False
        delay = 10
        super().__init__(image_fps, width, height, flip, delay)

    def update(self, entity):
        super().update(entity)
        if entity.velocity[1] == 0:
            self.context.transition_to(PlayerIdleLeft())
        elif entity.velocity[0] > 0.:
            self.context.transition_to(PlayerFallRight())
