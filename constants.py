# Game Constants and Enums
from enum import Enum

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PORTAL_TRANSITION = 3

class WorldType(Enum):
    DESERT = 0
    ICE = 1
    FOREST = 2

class Lane(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

# Lane positions
LANE_POSITIONS = {
    Lane.LEFT: -2.5,
    Lane.CENTER: 0.0,
    Lane.RIGHT: 2.5
}

# Lane switching
LANE_SWITCH_SPEED = 0.3  # How fast player moves between lanes

# Game Configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CHUNK_LENGTH = 50
TRANSITION_DURATION = 2.0
CAMERA_DISTANCE = 5

# Player Settings
PLAYER_SPEED = 0.15  # Not used for lane movement anymore
PLATFORM_SPEED = 0.2
JUMP_HEIGHT_MAX = 1.2
JUMP_SPEED = 0.1

# World Colors
WORLD_COLORS = {
    WorldType.DESERT: (0.9, 0.8, 0.5, 1.0),
    WorldType.ICE: (0.8, 0.9, 1.0, 1.0),
    WorldType.FOREST: (0.2, 0.6, 0.3, 1.0)
}

# Texture Mappings
WORLD_TEXTURES = {
    WorldType.DESERT: "desert_platform",
    WorldType.ICE: "ice_platform",
    WorldType.FOREST: "forest_platform"
}

# Generation Parameters
PORTAL_CHANCE = 0.3  # 30% chance per chunk
COIN_CHANCE = 0.7    # 70% chance per platform
GAP_CHANCE = 0.2     # 20% chance of gap between platforms

# Platform Settings (updated for 3-lane system)
PLATFORM_WIDTH = 8.0  # Wide enough for all 3 lanes
MIN_PLATFORM_LENGTH = 8.0
MAX_PLATFORM_LENGTH = 15.0

# Scoring
COIN_SCORE = 10
PORTAL_SCORE = 50

# Physics
GROUND_LEVEL = 0
COLLISION_TOLERANCE = 0.6