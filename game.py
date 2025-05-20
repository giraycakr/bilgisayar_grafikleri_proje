#!/usr/bin/env python3
"""
Main Game class for Portal Runner
"""
import os
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *

from audio import AudioManager
from constants import *
from player import Player
from world import WorldManager
from textures import TextureManager
from renderer import Renderer

import json


# Add these methods to the PortalRunner class
def load_high_scores(self):
    """Load high scores from JSON file"""
    self.high_scores = []
    try:
        with open("high_scores.json", "r") as f:
            self.high_scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create a new high scores file if it doesn't exist
        self.high_scores = []
        self.save_high_scores()


def save_high_scores(self):
    """Save high scores to JSON file"""
    with open("high_scores.json", "w") as f:
        json.dump(self.high_scores, f)


def add_high_score(self, name, score):
    """Add a new high score"""
    # Add the new score
    new_entry = {"name": name, "score": score}
    self.high_scores.append(new_entry)

    # Sort high scores (highest first)
    self.high_scores.sort(key=lambda x: x["score"], reverse=True)

    # Keep only top 5 scores
    self.high_scores = self.high_scores[:5]

    # Save to file
    self.save_high_scores()
class PortalRunner:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self.coyote_time = 0.08
        self.width = width
        self.height = height
        self.game_state = GameState.MENU
        self.score = 0
        self.high_score = 0

        # Player name and high scores
        self.player_name = ""
        self.input_active = False

        # Game objects
        self.player = Player()
        self.world_manager = WorldManager()
        self.texture_manager = TextureManager()
        self.renderer = Renderer(self.texture_manager)

        # Audio
        self.audio_manager = AudioManager()

        # Portal transition variables
        self.transition_start_time = 0
        self.next_world = None

        # Load high scores
        self.load_high_scores()

    def load_high_scores(self):
        """Load high scores from JSON file"""
        self.high_scores = []
        try:
            with open("high_scores.json", "r") as f:
                self.high_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create a new high scores file if it doesn't exist
            self.high_scores = []
            self.save_high_scores()

    def save_high_scores(self):
        """Save high scores to JSON file"""
        with open("high_scores.json", "w") as f:
            json.dump(self.high_scores, f)

    def add_high_score(self, name, score):
        """Add a new high score"""
        # Add the new score
        new_entry = {"name": name, "score": score}
        self.high_scores.append(new_entry)

        # Sort high scores (highest first)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)

        # Keep only top 5 scores
        self.high_scores = self.high_scores[:5]

        # Save to file
        self.save_high_scores()

    def init(self):
        """Initialize the game"""
        self.renderer.init_gl()
        self.texture_manager.init_all_textures()
        self.world_manager.reset()

        # Initialize audio
        os.makedirs("music", exist_ok=True)
        if self.audio_manager.load_background_music("music/background.mp3"):
            self.audio_manager.play_background_music(loop=True)
        else:
            print("No background music found. Create a 'music' folder and add 'background.mp3'")

    def init_audio(self):
        """Initialize audio"""
        # Check if music file exists, if not, we'll just proceed without music
        if self.audio_manager.load_background_music("music/background.mp3"):
            self.audio_manager.play_background_music(loop=True)
        else:
            print("Background music not found, continuing without music")
            # Try to create music directory for future use
            os.makedirs("music", exist_ok=True)

    def reset_game(self):
        """Reset the game for a new run"""
        # Check if previous score is a high score
        if self.game_state == GameState.GAME_OVER and self.score > 0:
            # If no high scores yet or score is better than lowest high score
            if not self.high_scores or len(self.high_scores) < 5 or self.score > min(
                    entry["score"] for entry in self.high_scores):
                # Make sure we have a player name
                if not self.player_name:
                    self.player_name = "Player"
                self.add_high_score(self.player_name, self.score)

        # Reset game state
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

        # Draw name input
        glColor3f(1.0, 1.0, 1.0)  # White
        self.renderer.draw_centered_text(self.height // 2 + 60, "Enter Your Name:", self.width)

        # Highlight input box if active
        if self.input_active:
            glColor3f(0.0, 1.0, 0.0)  # Green for active input
        else:
            glColor3f(0.7, 0.7, 0.7)  # Gray for inactive input

        # Draw input box
        input_text = self.player_name + ("_" if self.input_active else "")
        self.renderer.draw_centered_text(self.height // 2 + 30, input_text, self.width)

        # Instructions
        glColor3f(1.0, 1.0, 1.0)  # White
        self.renderer.draw_centered_text(self.height // 2, "Click to input name, ENTER to confirm", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 30, "Press SPACE to start", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 60, "Use A/D to switch lanes, W to jump, S to quick land",
                                         self.width)

        # Draw high scores
        if self.high_scores:
            glColor3f(1.0, 1.0, 0.0)  # Yellow
            self.renderer.draw_centered_text(self.height // 2 - 100, "HIGH SCORES", self.width)

            for i, entry in enumerate(self.high_scores[:5]):
                glColor3f(1.0, 1.0, 1.0)  # White
                score_text = f"{i + 1}. {entry['name']}: {entry['score']}"
                self.renderer.draw_centered_text(self.height // 2 - 130 - (i * 20), score_text, self.width)

        self.renderer.restore_3d_projection()

    def render_game_over(self):
        """Render game over screen"""
        self.renderer.setup_2d_projection(self.width, self.height)

        # Draw game over text
        glColor3f(1.0, 0.0, 0.0)  # Red
        self.renderer.draw_centered_text(self.height - 100, "GAME OVER", self.width)

        # Draw final score
        glColor3f(1.0, 1.0, 1.0)  # White
        self.renderer.draw_centered_text(self.height // 2 + 30, f"Final Score: {self.score}", self.width)
        self.renderer.draw_centered_text(self.height // 2, f"Distance Traveled: {int(-self.player.z)}", self.width)
        self.renderer.draw_centered_text(self.height // 2 - 30, "Press SPACE to restart", self.width)

        # Draw high scores
        if self.high_scores:
            glColor3f(1.0, 1.0, 0.0)  # Yellow
            self.renderer.draw_centered_text(self.height // 2 - 80, "HIGH SCORES", self.width)

            for i, entry in enumerate(self.high_scores[:5]):
                glColor3f(1.0, 1.0, 1.0)  # White
                score_text = f"{i + 1}. {entry['name']}: {entry['score']}"
                self.renderer.draw_centered_text(self.height // 2 - 110 - (i * 20), score_text, self.width)

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
                self.player.jump()
            elif key == 's':
                self.player.quick_land()  # Add this line
        elif self.game_state in [GameState.MENU, GameState.GAME_OVER]:
            if key == ' ':
                self.reset_game()

    def handle_special_key(self, key):
        """Handle special key press (arrow keys)"""
        if self.game_state == GameState.PLAYING:
            from OpenGL.GLUT import GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_KEY_DOWN

            if key == GLUT_KEY_LEFT:
                self.player.move_left()
            elif key == GLUT_KEY_RIGHT:
                self.player.move_right()
            elif key == GLUT_KEY_UP:
                self.player.jump()
            elif key == GLUT_KEY_DOWN:
                self.player.quick_land()