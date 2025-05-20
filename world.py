#!/usr/bin/env python3
"""
World and platform generation for Portal Runner
"""

import random
import math
import time
from constants import *


class SpeedManager:
    """Manages progressive speed increase"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset speed to base values"""
        self.current_platform_speed = BASE_PLATFORM_SPEED
        self.current_lane_switch_speed = BASE_LANE_SWITCH_SPEED
        self.speed_multiplier = 1.0

    def update(self, distance_traveled):
        """Update speed based on distance traveled"""
        # Calculate speed multiplier based on distance (every SPEED_INCREASE_INTERVAL units increases speed)
        speed_increase = (abs(distance_traveled) // SPEED_INCREASE_INTERVAL) * SPEED_INCREASE_RATE
        self.speed_multiplier = 1.0 + speed_increase

        # Apply speed multiplier with caps
        self.current_platform_speed = min(
            BASE_PLATFORM_SPEED * self.speed_multiplier,
            MAX_PLATFORM_SPEED
        )

        self.current_lane_switch_speed = min(
            BASE_LANE_SWITCH_SPEED * self.speed_multiplier,
            MAX_LANE_SWITCH_SPEED
        )

    def get_platform_speed(self):
        """Get current platform speed"""
        return self.current_platform_speed

    def get_lane_switch_speed(self):
        """Get current lane switch speed"""
        return self.current_lane_switch_speed

    def get_speed_multiplier(self):
        """Get current speed multiplier for display"""
        return self.speed_multiplier


class PlatformChunk:
    """Represents a chunk of platforms, coins, and portals"""

    def __init__(self, start_z, chunk_id):
        self.start_z = start_z
        self.chunk_id = chunk_id
        self.platforms = []
        self.coins = []
        self.portals = []
        self.generate_platforms()
        self.generate_coins()
        self.maybe_add_portal()

    # Modified code for world.py
    def generate_platforms(self):
        """Generate platforms for this chunk"""
        current_z = self.start_z

        # Ensure first platform is always at the chunk start for initial chunks
        if self.chunk_id < 3:  # First few chunks should have guaranteed platforms
            width = PLATFORM_WIDTH  # Use consistent width for 3-lane system
            length = 10.0
            x_offset = 0  # Always centered for 3-lane system

            platform = {
                'x': x_offset,
                'y': GROUND_LEVEL,
                'z': current_z,
                'width': width,
                'length': length
            }
            self.platforms.append(platform)
            current_z -= length

        # Generate rest of platforms normally
        while current_z > self.start_z - CHUNK_LENGTH:
            # Fixed width for 3-lane system, random length
            width = PLATFORM_WIDTH
            length = random.uniform(MIN_PLATFORM_LENGTH, MAX_PLATFORM_LENGTH)

            # Always centered for 3-lane system
            x_offset = 0

            # Create platform
            platform = {
                'x': x_offset,
                'y': GROUND_LEVEL,
                'z': current_z,
                'width': width,
                'length': length
            }
            self.platforms.append(platform)

            # Move to next platform position
            current_z -= length

            # Always add a gap between platforms, with size based on chunk_id (difficulty)
            # Calculate maximum safe jump distance based on current platform speed
            platform_speed = BASE_PLATFORM_SPEED * (1.0 + min(self.chunk_id * SPEED_INCREASE_RATE, 4.0))
            max_jump_distance = platform_speed * 24 * 0.8  # 80% of theoretical max jump distance for safety

            # Cap the max gap to be jumpable
            min_gap = max(0.5, min(0.8 + self.chunk_id * 0.05, 1.5))  # Starts at 0.5-0.8, max 1.5
            max_gap = max(1.0, min(1.5 + self.chunk_id * 0.1, 3.0))  # Starts at 1.0-1.5, max 3.0

            # Add gap - always present but size varies
            gap = random.uniform(min_gap, max_gap)
            current_z -= gap
    def generate_coins(self):
        """Generate coins on platforms aligned with lanes"""
        for platform in self.platforms:
            # Chance of having coins on a platform
            if random.random() < COIN_CHANCE:
                # Generate coins in lanes
                for lane in [Lane.LEFT, Lane.CENTER, Lane.RIGHT]:
                    # 60% chance for each lane to have a coin
                    if random.random() < 0.6:
                        coin_x = LANE_POSITIONS[lane]
                        coin_z = platform['z'] - random.uniform(1, platform['length'] - 1)

                        coin = {
                            'x': coin_x,
                            'y': platform['y'] + 0.5,
                            'z': coin_z,
                            'rotation': random.uniform(0, 360),
                            'collected': False,
                            'lane': lane  # Track which lane this coin is in
                        }
                        self.coins.append(coin)

    def maybe_add_portal(self):
        """Chance to add a portal to this chunk"""
        # Only add portals after the first few chunks
        if self.chunk_id < 3:
            return

        if random.random() < PORTAL_CHANCE and self.platforms:
            # Choose a platform for the portal
            platform = random.choice(self.platforms)

            # Place portal in center lane
            portal = {
                'x': LANE_POSITIONS[Lane.CENTER],  # Always in center lane
                'y': platform['y'] + 1.5,  # Higher up to be more visible
                'z': platform['z'] - platform['length'] / 2,
                'rotation': 0,
                'scale': 1.0
            }
            self.portals.append(portal)

    def update(self):
        """Update rotating objects in this chunk"""
        # Update coin rotations
        for coin in self.coins:
            coin['rotation'] = (coin['rotation'] + 5) % 360

        # Update portal rotations and scaling
        for portal in self.portals:
            portal['rotation'] = (portal['rotation'] + 1) % 360
            portal['scale'] = 1.0 + 0.1 * math.sin(time.time() * 2)


class WorldManager:
    """Manages the infinite world generation"""

    def __init__(self):
        self.current_world = WorldType.DESERT
        self.platform_chunks = []
        self.last_chunk_z = 0
        self.chunk_counter = 0
        self.speed_manager = SpeedManager()

    def reset(self):
        """Reset world for new game"""
        self.platform_chunks = []
        self.last_chunk_z = 0
        self.chunk_counter = 0
        self.speed_manager.reset()
        self.generate_initial_chunks()

    def generate_initial_chunks(self):
        """Generate initial chunks for the game"""
        # Generate chunks both ahead and behind the starting position
        for i in range(-2, 8):  # Generate from 2 chunks behind to 7 chunks ahead
            chunk_start = i * CHUNK_LENGTH
            self.platform_chunks.append(self.generate_chunk(chunk_start))
            self.last_chunk_z = chunk_start

    def generate_chunk(self, start_z):
        """Generate a new platform chunk"""
        chunk = PlatformChunk(start_z, self.chunk_counter)
        self.chunk_counter += 1
        return chunk

    def update(self, player_z):
        """Update world generation and remove old chunks"""
        # Update speed based on distance traveled
        self.speed_manager.update(player_z)

        # Generate new chunks ahead of the player
        while self.last_chunk_z > player_z - CHUNK_LENGTH * 3:
            self.last_chunk_z -= CHUNK_LENGTH
            new_chunk = self.generate_chunk(self.last_chunk_z)
            self.platform_chunks.append(new_chunk)

        # Remove old chunks that are far behind (increased distance)
        self.platform_chunks = [chunk for chunk in self.platform_chunks
                                if chunk.start_z > player_z - CHUNK_LENGTH * 5]

        # Update all chunks
        for chunk in self.platform_chunks:
            chunk.update()

    def get_current_speed(self):
        """Get current platform speed"""
        return self.speed_manager.get_platform_speed()

    def get_lane_switch_speed(self):
        """Get current lane switch speed"""
        return self.speed_manager.get_lane_switch_speed()

    def get_speed_multiplier(self):
        """Get current speed multiplier"""
        return self.speed_manager.get_speed_multiplier()

    def check_platform_collision(self, player):
        """Check if player is on a platform"""
        player_bounds = player.get_bounding_box()

        # Add a minimal edge grace distance
        edge_grace = 0.2  # Very small forgiveness at platform edges

        for chunk in self.platform_chunks:
            for platform in chunk.platforms:
                platform_bounds = {
                    'min_x': platform['x'] - platform['width'] / 2,
                    'max_x': platform['x'] + platform['width'] / 2,
                    'min_z': platform['z'] - platform['length'] - edge_grace,  # Small extension
                    'max_z': platform['z'] + edge_grace,  # Small extension
                    'y': platform['y']
                }

                # Check if player is above platform (horizontally)
                if (player_bounds['min_x'] <= platform_bounds['max_x'] and
                        player_bounds['max_x'] >= platform_bounds['min_x'] and
                        player_bounds['min_z'] <= platform_bounds['max_z'] and
                        player_bounds['max_z'] >= platform_bounds['min_z']):

                    # Check vertical position with standard tolerance
                    vertical_tolerance = COLLISION_TOLERANCE
                    if abs(player_bounds['y'] - platform_bounds['y']) < vertical_tolerance:
                        return True

        return False
    def check_coin_collection(self, player):
        """Check for coin collection and return collected coins"""
        collected_coins = []
        player_pos = player.get_position()

        for chunk in self.platform_chunks:
            for coin in chunk.coins:
                if not coin['collected']:
                    # Calculate distance between player and coin
                    dx = player_pos[0] - coin['x']
                    dz = player_pos[2] - coin['z']
                    dy = player_pos[1] - coin['y']
                    distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                    # If player is close enough, collect the coin
                    if distance < 0.7:
                        coin['collected'] = True
                        collected_coins.append(coin)

        return collected_coins

    def check_portal_interaction(self, player):
        """Check for portal interaction"""
        player_pos = player.get_position()

        for chunk in self.platform_chunks:
            for portal in chunk.portals:
                # Calculate distance between player and portal
                dx = player_pos[0] - portal['x']
                dz = player_pos[2] - portal['z']
                dy = player_pos[1] - portal['y']
                distance = math.sqrt(dx * dx + dz * dz)

                # Check if player is close enough and at similar height
                if distance < 2.0 and abs(dy) < 1.5:  # Increased radius, check height
                    return portal

        return None

    def get_world_color(self):
        """Get current world color"""
        return WORLD_COLORS[self.current_world]

    def get_world_texture_name(self):
        """Get current world texture name"""
        return WORLD_TEXTURES[self.current_world]

    def set_world(self, world_type):
        """Set the current world type"""
        self.current_world = world_type