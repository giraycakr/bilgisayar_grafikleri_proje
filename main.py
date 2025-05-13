#!/usr/bin/env python3
"""
Portal Runner - Main Entry Point
A 3D infinite runner game with portals between different worlds
"""

import sys
from OpenGL.GLUT import *

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
    # Convert bytes to string for regular keys
    if isinstance(key, bytes):
        key = key.decode('utf-8').lower()
    else:
        key = chr(key).lower()

    game.handle_key(key)

    # Quit on ESC
    if key == chr(27):  # ESC
        sys.exit(0)


def special_keys(key, x, y):
    """GLUT special keys callback (arrow keys)"""
    game.handle_special_key(key)


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