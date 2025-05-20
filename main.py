#!/usr/bin/env python3
"""
Portal Runner - Main Entry Point
A 3D infinite runner game with portals between different worlds
"""
#!/usr/bin/env python3
"""
Main Game class for Portal Runner
"""

import random
import time
import json
import os
from OpenGL.GL import *
from OpenGL.GLU import *

from constants import *
from player import Player
from world import WorldManager
from textures import TextureManager
from renderer import Renderer
from audio import AudioManager
import sys
from OpenGL.GLUT import *

from constants import GameState
from game import PortalRunner

# Global game instance
game = None


def display():
    """GLUT display callback"""
    game.render()
    glutSwapBuffers()


def reshape(width, height):
    """GLUT reshape callback"""
    game.reshape(width, height)


def keyboard(key, x, y):
    """GLUT keyboard callback"""
    # Handle text input for player name
    if game.game_state == GameState.MENU and game.input_active:
        # Convert key to integer ordinal if it's bytes
        key_code = ord(key) if isinstance(key, bytes) else ord(key)

        # Check for Enter key
        if key_code == 13 or key_code == 10:  # Enter key (CR or LF)
            game.input_active = False
        # Check for Backspace (multiple possible codes)
        elif key_code == 8 or key_code == 127:  # Backspace or Delete
            if len(game.player_name) > 0:
                game.player_name = game.player_name[:-1]
        # Regular character input
        elif 32 <= key_code <= 126 and len(game.player_name) < 15:  # Printable ASCII
            if isinstance(key, bytes):
                game.player_name += key.decode('utf-8')
            else:
                game.player_name += key
    else:
        # Convert to lowercase for normal game controls
        if isinstance(key, bytes):
            key = key.decode('utf-8').lower()
        else:
            key = key.lower()
        game.handle_key(key)

    # Quit on ESC
    if (isinstance(key, bytes) and key == b'\x1b') or key == chr(27):  # ESC
        sys.exit(0)

def mouse(button, state, x, y):
    """GLUT mouse callback"""
    if game.game_state == GameState.MENU:
        from OpenGL.GLUT import GLUT_LEFT_BUTTON, GLUT_DOWN
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Calculate y position in our coordinate system
            y = game.height - y

            # Check if click is in the input area
            input_y = game.height // 2 + 30
            if abs(y - input_y) < 15:
                game.input_active = True
            else:
                game.input_active = False
def special_keys(key, x, y):
    """GLUT special keys callback (arrow keys)"""
    from OpenGL.GLUT import GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_KEY_DOWN

    if key == GLUT_KEY_LEFT:
        game.player.move_left()
    elif key == GLUT_KEY_RIGHT:
        game.player.move_right()
    elif key == GLUT_KEY_UP:
        game.player.jump()
    elif key == GLUT_KEY_DOWN:
        game.player.quick_land()


def idle():
    """GLUT idle callback for animation"""
    game.update()
    glutPostRedisplay()


def main():
    """Main function to initialize and start the game"""
    global game

    # Print start message
    print("Starting Portal Runner...")
    print("Controls:")
    print("  A/D or Left/Right arrows - Move left/right")
    print("  W or Up arrow - Jump")
    print("  S or Down arrow - Quick land")
    print("  Space - Start/Restart game")
    print("  ESC - Quit")
    print()

    # Initialize GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Portal Runner - Infinite Edition")

    # Create game instance
    game = PortalRunner()
    game.init()

    # Set up GLUT callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)  # Add this line
    glutIdleFunc(idle)

    print("Game initialized successfully!")
    print("Starting main loop...")

    # Start main loop
    try:
        glutMainLoop()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error during game execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()