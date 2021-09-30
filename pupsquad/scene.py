"""Game scenes and their context manager."""
import abc

import pygame

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

    def run(self, screen):
        """Run the game."""
        # Initialize the frame rate clock.
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


class Scene(abc.ABC):
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


class Level(Scene):
    """A game level."""

    def __init__(self, player, decor):
        self.player = player
        self.decor = decor

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self):
        # Calculate the time delta for physics calculations.
        self.player.update(self)

    def draw(self, screen):
        screen.fill(pygame.Color("grey"))
        self.decor.draw(screen)
        self.player.draw(screen)
