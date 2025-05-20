#!/usr/bin/env python3
"""
Audio management for Portal Runner
"""

import os
import pygame


class AudioManager:
    def __init__(self):
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            self.initialized = True
        except:
            print("Warning: Could not initialize audio. Game will run without sound.")
            self.initialized = False

        self.music_playing = False

    def load_background_music(self, filename):
        """Load background music"""
        if not self.initialized:
            return False

        if os.path.exists(filename):
            try:
                pygame.mixer.music.load(filename)
                return True
            except Exception as e:
                print(f"Error loading music {filename}: {e}")
        else:
            print(f"Music file not found: {filename}")
        return False

    def play_background_music(self, loop=True):
        """Play background music"""
        if not self.initialized:
            return

        if pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.play(-1 if loop else 0)
            self.music_playing = True
        except Exception as e:
            print(f"Error playing music: {e}")

    def stop_background_music(self):
        """Stop background music"""
        if not self.initialized:
            return

        pygame.mixer.music.stop()
        self.music_playing = False