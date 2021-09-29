"""Game scenes and their context manager."""
import abc
import datetime

import pygame

from pupsquad.constant import SCREEN_WIDTH
from pupsquad.constant import SCREEN_HEIGHT
from pupsquad.constant import FRAMERATE


class SceneContext:
    """The scene context class."""

    _scene = None
    """The current scene of the game."""

    def __init__(self, scene):
        self.transition_to(scene)

    def transition_to(self, scene):
        """Transition to another scene."""
        self._scene = scene
        self._scene.context = self

    def run(self):
        """Run the game."""
        # Initialize the screen object and frame rate clock.
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

        # Main game loop.
        while True:
            # Handle events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self._scene.handle_event(event)
            # Update state.
            self._scene.update()
            # Draw.
            self._scene.draw(screen)
            pygame.display.flip()
            clock.tick(FRAMERATE)


class AbstractScene(abc.ABC):
    """Abstract base class for a game scene."""

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @abc.abstractmethod
    def handle_event(self, event):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self, screen):
        pass


class Level(AbstractScene):
    """A game level."""

    def __init__(self, player, decor):
        self.player = player
        self.decor = decor
        self.previous_time = None

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self):
        # Calculate the time delta for physics calculations.
        current_time = datetime.datetime.now()
        time_delta = 0.
        if self.previous_time is not None:
            time_delta = (current_time-self.previous_time).total_seconds()
        self.previous_time = current_time
        # Update the entities.
        self.player.update(time_delta, self.decor)

    def draw(self, screen):
        screen.fill(pygame.Color("grey"))
        self.decor.draw(screen)
        self.player.draw(screen)
