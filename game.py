#!/usr/bin/env python3
"""
Main Game class for Portal Runner
"""

import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *

from constants import *
from player import Player
from world import WorldManager
from textures import TextureManager
from renderer import Renderer


class PortalRunner:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.game_state = GameState.MENU
        self.score = 0
        self.high_score = 0
        self.last_on_platform = 0  # Add this line to track when player was last on platform
        self.coyote_time = 0.08  # Allow jumping for 0.15 seconds after leaving platform

        # Game objects
        self.player = Player()
        self.world_manager = WorldManager()
        self.texture_manager = TextureManager()
        self.renderer = Renderer(self.texture_manager)

        # Portal transition variables
        self.transition_start_time = 0
        self.next_world = None

    def init(self):
        """Initialize the game"""
        self.renderer.init_gl()
        self.texture_manager.init_all_textures()
        self.world_manager.reset()

    def reset_game(self):
        """Reset the game for a new run"""
        self.player.reset()
        self.world_manager.reset()
        self.score = 0
        self.game_state = GameState.PLAYING

    def update(self):
        """Update game state"""
        if self.game_state == GameState.PLAYING:
            self.update_playing()
        elif self.game_state == GameState.PORTAL_TRANSITION:
            self.update_portal_transition()

    def update_playing(self):
        """Update game when playing"""
        current_time = time.time()

        # Get current speeds from world manager
        platform_speed = self.world_manager.get_current_speed()
        lane_switch_speed = self.world_manager.get_lane_switch_speed()

        # Update player with dynamic speeds
        self.player.update(platform_speed, lane_switch_speed)

        # Update world
        self.world_manager.update(self.player.z)

        # Check platform collision - be more lenient with jumping players
        on_platform = self.world_manager.check_platform_collision(self.player)

        # Update last_on_platform time if currently on platform
        if on_platform:
            self.last_on_platform = current_time

        # Only end game if player is falling, not on platform, AND coyote time expired
        if not on_platform:
            # Check if we're in coyote time (recently left platform)
            in_coyote_time = (current_time - self.last_on_platform) < self.coyote_time

            # If player is jumping, recently jumped, or in coyote time, don't end game
            if self.player.is_jumping or self.player.jump_height > 0.1 or in_coyote_time:
                # Player is either jumping or recently left platform, don't end game
                pass
            else:
                # Player is on the ground, not on a platform, and coyote time expired
                self.game_state = GameState.GAME_OVER
                if self.score > self.high_score:
                    self.high_score = self.score

        # Check coin collection
        collected_coins = self.world_manager.check_coin_collection(self.player)
        for coin in collected_coins:
            self.score += COIN_SCORE

        # Check portal interaction
        portal = self.world_manager.check_portal_interaction(self.player)
        if portal:
            self.start_portal_transition()

    def start_portal_transition(self):
        """Start portal transition"""
        # Prevent multiple portal transitions
        if self.game_state == GameState.PORTAL_TRANSITION:
            return

        self.game_state = GameState.PORTAL_TRANSITION
        self.transition_start_time = time.time()

        # Choose next world (different from current)
        current = self.world_manager.current_world
        possible_worlds = [w for w in WorldType if w != current]
        self.next_world = random.choice(possible_worlds)

        # Give score bonus for using portal
        self.score += PORTAL_SCORE

        # Remove all portals in the current vicinity to prevent re-triggering
        player_z = self.player.z
        for chunk in self.world_manager.platform_chunks:
            chunk.portals = [p for p in chunk.portals
                             if abs(p['z'] - player_z) > 10]  # Remove nearby portals

    def update_portal_transition(self):
        """Update portal transition"""
        if self.transition_start_time == 0:
            # Safety check - if somehow we're in transition without start time
            self.game_state = GameState.PLAYING
            return

        current_time = time.time()
        progress = min(1.0, (current_time - self.transition_start_time) / TRANSITION_DURATION)

        if progress >= 1.0:
            # Transition complete
            self.world_manager.set_world(self.next_world)
            self.game_state = GameState.PLAYING
            self.transition_start_time = 0  # Reset for safety
            self.next_world = None

    def render(self):
        """Render the game"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.game_state == GameState.MENU:
            self.render_menu()
        elif self.game_state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.game_state == GameState.PORTAL_TRANSITION:
            self.render_portal_transition()
        else:  # PLAYING
            self.render_playing()

    def render_playing(self):
        """Render the game while playing"""
        # Set up 3D projection
        self.renderer.setup_3d_projection(self.width, self.height)
        glLoadIdentity()

        # Ensure proper lighting state before rendering
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glColor3f(1.0, 1.0, 1.0)

        # Position camera behind player with better angle to see gaps
        player_pos = self.player.get_position()
        gluLookAt(
            player_pos[0], player_pos[1] + 2.5, player_pos[2] + CAMERA_DISTANCE,  # Higher eye position
            player_pos[0], player_pos[1], player_pos[2] - 10,  # Looking further ahead
            0, 1, 0  # Up vector
        )

        # Update light position after setting camera
        light_position = [player_pos[0] + 5.0, player_pos[1] + 10.0, player_pos[2] + 5.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Draw world and player
        self.renderer.draw_world(self.world_manager, self.player)
        self.renderer.draw_player(self.player)

        # Draw UI
        self.render_ui()

    def render_ui(self):
        """Render game UI (minimal, focused on gameplay)"""
        self.renderer.setup_2d_projection(self.width, self.height)

        # Just the essential info
        glColor3f(1.0, 1.0, 1.0)
        self.renderer.draw_text(10, self.height - 20, f"Score: {self.score}")
        self.renderer.draw_text(10, self.height - 40, f"Distance: {int(-self.player.z)}")

        # Show speed multiplier only
        speed_multiplier = self.world_manager.get_speed_multiplier()
        glColor3f(1.0, 1.0, 0.0)  # Yellow for speed
        self.renderer.draw_text(10, self.height - 60, f"Speed: {speed_multiplier:.1f}x")

        self.renderer.restore_3d_projection()

    # Remove the speed bar and lane indicator methods - focusing on gameplay only

    def render_menu(self):
        """Render main menu"""
        self.renderer.setup_2d_projection(self.width, self.height)

        # Draw title
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        self.renderer.draw_centered_text(self.height - 100, "PORTAL RUNNER - 3 LANES", self.width)

        # Draw instructions
        glColor3f(1.0, 1.0, 1.0)  # White
        self.renderer.draw_centered_text(self.height // 2, "Press SPACE to start", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 30, "Use A/D to switch lanes, W to jump", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 60, "Run through 3 lanes and collect coins!", self.width)

        self.renderer.restore_3d_projection()

    def render_game_over(self):
        """Render game over screen"""
        self.renderer.setup_2d_projection(self.width, self.height)

        # Draw game over text
        glColor3f(1.0, 0.0, 0.0)  # Red
        self.renderer.draw_centered_text(self.height - 100, "GAME OVER", self.width)

        # Draw final score
        glColor3f(1.0, 1.0, 1.0)  # White
        self.renderer.draw_centered_text(self.height // 2, f"Final Score: {self.score}", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 30, f"Distance Traveled: {int(-self.player.z)}", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 60, "Press SPACE to restart", self.width)

        self.renderer.restore_3d_projection()

    def render_portal_transition(self):
        """Render portal transition effect"""
        current_time = time.time()
        progress = min(1.0, (current_time - self.transition_start_time) / TRANSITION_DURATION)

        self.renderer.draw_portal_transition(progress, self.next_world, self.width, self.height)

    def reshape(self, width, height):
        """Handle window resizing"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def handle_key(self, key):
        """Handle key press"""
        if self.game_state == GameState.PLAYING:
            if key == 'a':
                self.player.move_left()
            elif key == 'd':
                self.player.move_right()
            elif key == 'w':
                # Allow jumping during coyote time
                coyote_jump = (time.time() - self.last_on_platform) < self.coyote_time
                self.player.jump(allow_coyote_jump=coyote_jump)
            elif key == 's':
                self.player.quick_land()
        elif self.game_state in [GameState.MENU, GameState.GAME_OVER]:
            if key == ' ':
                self.reset_game()

    def handle_special_key(self, key):
        """Handle special key press (arrow keys)"""
        if self.game_state == GameState.PLAYING:
            from OpenGL.GLUT import GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP

            if key == GLUT_KEY_LEFT:
                self.player.move_left()
            elif key == GLUT_KEY_RIGHT:
                self.player.move_right()
            elif key == GLUT_KEY_UP:
                self.player.jump()