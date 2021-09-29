"""Pup Squad: A totally-not-Paw-Patrol platformer for kids."""
import abc
import datetime

import numpy as np
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAMERATE = 60

METERS = 100  ## Amount of pixels per meter.
GRAVITY = 9.81*METERS
TILE_SIZE = 0.25*METERS

#
# MAIN GAME CONTEXT MANAGER
#


class GameContextManager:
    """The game state machine's main context class."""

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


#
# GAME SCENES
#


class GameScene(abc.ABC):
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


class Level(GameScene):
    """Base class for the game's levels."""

    def __init__(self, player, level_map):
        self.player = player
        self.level_map = level_map
        self.previous_time = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_a:
                self.player.start_run_left()
            elif event.key == pygame.K_d:
                self.player.start_run_right()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.player.stop_run_left()
            elif event.key == pygame.K_d:
                self.player.stop_run_right()

    def update(self):
        # Calculate the time delta for physics calculations.
        current_time = datetime.datetime.now()
        time_delta = 0.
        if self.previous_time is not None:
            time_delta = (current_time-self.previous_time).total_seconds()
        self.previous_time = current_time
        # Update the entities.
        self.player.update(time_delta, self.level_map)

    def draw(self, screen):
        screen.fill(pygame.Color("grey"))
        self.level_map.draw(screen)
        self.player.draw(screen)


class LevelOne(Level):
    """The first level of the game."""

    def __init__(self):
        player_position = np.array([2.*METERS, 5.8*METERS])
        player = Player(player_position)
        level_map = LevelOneMap()
        super().__init__(player, level_map)


#
# ENTITIES
#


class GameEntity(pygame.sprite.Sprite):
    """Base class for game entities."""

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

    def update(self, time_delta, level_map):
        """Update the entity state."""
        # Calculate position delta.
        acceleration = self.force/self.mass - [0., GRAVITY]
        self.velocity += acceleration*time_delta
        position_delta = np.round(self.velocity*time_delta)
        position_delta *= np.array([1, -1])
        # Check for collision with impassable map sprites.
        for tile in level_map.tiles:
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


class Player(GameEntity):
    """The player entity."""

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


#
# MAPS
#


class MapTile(pygame.sprite.Sprite):
    """A tile in a map."""

    def __init__(self, tile_type, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x*TILE_SIZE, y*TILE_SIZE)
        if tile_type == 0:
            self.image.fill(pygame.Color("grey"))
            self.passable = True
        else:
            self.image.fill(pygame.Color("black"))
            self.passable = False


class Map:
    """Base class for the game's maps."""

    def __init__(self, tile_grid):
        self.tiles = pygame.sprite.Group()
        for y, tile_column in enumerate(tile_grid):
            for x, tile_type in enumerate(tile_column):
                tile = MapTile(tile_type, x, y)
                self.tiles.add(tile)

    def draw(self, screen):
        self.tiles.draw(screen)


class LevelOneMap(Map):
    """The map of the first level."""

    def __init__(self):
        tile_grid = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ])
        super().__init__(tile_grid)


def main():
    """Main execution function."""
    game = GameContextManager(LevelOne())
    game.run()


if __name__ == "__main__":
    main()
