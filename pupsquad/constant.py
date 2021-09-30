"""Application constants."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAMERATE = 60
SECONDS_PER_FRAME = 1/FRAMERATE

METERS = 100  ## Amount of pixels per meter.
GRAVITY = 9.81*METERS
TILE_SIZE = 0.25*METERS
