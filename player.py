#!/usr/bin/env python3
"""
Player class for Portal Runner
"""

from constants import *


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset player to initial state"""
        self.x = 0
        self.y = 0.5
        self.z = 0
        self.jump_height = 0
        self.is_jumping = False

    def update(self):
        """Update player physics"""
        # Handle jump animation
        if self.is_jumping:
            self.jump_height += JUMP_SPEED
            if self.jump_height >= JUMP_HEIGHT_MAX:
                self.is_jumping = False
        elif self.jump_height > 0:
            self.jump_height -= JUMP_SPEED
            if self.jump_height < 0:
                self.jump_height = 0

        # Move player forward automatically
        self.z -= PLATFORM_SPEED

    def move_left(self):
        """Move player left"""
        self.x -= PLAYER_SPEED
        self.x = max(-5, self.x)  # Clamp to prevent going too far left

    def move_right(self):
        """Move player right"""
        self.x += PLAYER_SPEED
        self.x = min(5, self.x)  # Clamp to prevent going too far right

    def jump(self):
        """Make player jump if on ground"""
        if not self.is_jumping and self.jump_height == 0:
            self.is_jumping = True

    def get_position(self):
        """Get player's current position"""
        return (self.x, self.y + self.jump_height, self.z)

    def get_bounding_box(self):
        """Get player's bounding box for collision detection"""
        return {
            'min_x': self.x - 0.4,
            'max_x': self.x + 0.4,
            'min_z': self.z - 0.4,
            'max_z': self.z + 0.4,
            'y': self.y + self.jump_height
        }