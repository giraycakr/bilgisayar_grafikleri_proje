#!/usr/bin/env python3
"""
Player class for Portal Runner with 3-Lane System
"""

from constants import *


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset player to initial state"""
        self.current_lane = Lane.CENTER
        self.target_x = LANE_POSITIONS[self.current_lane]
        self.x = self.target_x
        self.y = 0.5
        self.z = 0
        self.jump_height = 0
        self.is_jumping = False
        self.is_moving_lanes = False

    def update(self, platform_speed, lane_switch_speed):
        """Update player physics with dynamic speeds"""
        # Handle jump animation
        if self.is_jumping:
            jump_speed = JUMP_SPEED * (
                        1 + (platform_speed - BASE_PLATFORM_SPEED) * 0.5)  # Slightly faster jumps at high speed
            self.jump_height += jump_speed
            if self.jump_height >= JUMP_HEIGHT_MAX:
                self.is_jumping = False
        elif self.jump_height > 0:
            jump_speed = JUMP_SPEED * (1 + (platform_speed - BASE_PLATFORM_SPEED) * 0.5)
            self.jump_height -= jump_speed
            if self.jump_height < 0:
                self.jump_height = 0

        # Handle lane movement (smooth transition between lanes)
        if self.is_moving_lanes:
            # Move towards target lane position with dynamic speed
            diff = self.target_x - self.x
            if abs(diff) > 0.1:
                # Still moving - use dynamic lane switch speed
                move_speed = lane_switch_speed
                if diff > 0:
                    self.x += move_speed
                    if self.x > self.target_x:
                        self.x = self.target_x
                else:
                    self.x -= move_speed
                    if self.x < self.target_x:
                        self.x = self.target_x
            else:
                # Reached target
                self.x = self.target_x
                self.is_moving_lanes = False

        # Move player forward automatically with dynamic speed
        self.z -= platform_speed

    def move_left(self):
        """Move player to left lane"""
        if self.current_lane == Lane.CENTER:
            self.current_lane = Lane.LEFT
            self.target_x = LANE_POSITIONS[Lane.LEFT]
            self.is_moving_lanes = True
        elif self.current_lane == Lane.RIGHT:
            self.current_lane = Lane.CENTER
            self.target_x = LANE_POSITIONS[Lane.CENTER]
            self.is_moving_lanes = True

    def move_right(self):
        """Move player to right lane"""
        if self.current_lane == Lane.CENTER:
            self.current_lane = Lane.RIGHT
            self.target_x = LANE_POSITIONS[Lane.RIGHT]
            self.is_moving_lanes = True
        elif self.current_lane == Lane.LEFT:
            self.current_lane = Lane.CENTER
            self.target_x = LANE_POSITIONS[Lane.CENTER]
            self.is_moving_lanes = True

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

    def get_current_lane(self):
        """Get current lane"""
        return self.current_lane