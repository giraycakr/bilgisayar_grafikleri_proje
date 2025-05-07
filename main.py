#!/usr/bin/env python3
"""
Portal Runner - A PyOpenGL 3D Game
Author: [Student Name]
Description: An endless runner game with portals between different worlds
"""

import sys
import os
import random
import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image

if not hasattr(OpenGL.GLUT, 'GLUT_BITMAP_HELVETICA_18'):
    GLUT_BITMAP_HELVETICA_18 = OpenGL.GLUT.glutBitmapHelvetica18
    GLUT_BITMAP_HELVETICA_12 = OpenGL.GLUT.glutBitmapHelvetica12
    GLUT_BITMAP_9_BY_15 = OpenGL.GLUT.glutBitmap9By15
    GLUT_BITMAP_8_BY_13 = OpenGL.GLUT.glutBitmap8By13
    GLUT_BITMAP_TIMES_ROMAN_10 = OpenGL.GLUT.glutBitmapTimesRoman10
    GLUT_BITMAP_TIMES_ROMAN_24 = OpenGL.GLUT.glutBitmapTimesRoman24
# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_PORTAL_TRANSITION = 3

# World Types
WORLD_DESERT = 0
WORLD_ICE = 1
WORLD_FOREST = 2

# Global variables
window_width = 800
window_height = 600
game_state = STATE_MENU
current_world = WORLD_DESERT
next_world = None
score = 0
high_score = 0
player_x = 0
player_y = 0.5  # Player height above platform
player_z = -5
player_speed = 0.1
platform_speed = 0.15
jump_height = 0
is_jumping = False
platforms = []
coins = []
portals = []
textures = {}
transition_start_time = 0
transition_duration = 2.0  # 2 seconds for portal transition
last_platform_z = -5  # Starting position for the first platform

# Colors
desert_color = (0.9, 0.8, 0.5, 1.0)  # Sandy beige
ice_color = (0.8, 0.9, 1.0, 1.0)  # Light blue
forest_color = (0.2, 0.6, 0.3, 1.0)  # Green


def load_texture(filename):
    """Load a texture from file and return its OpenGL ID"""
    try:
        img = Image.open(filename)
        img_data = np.array(list(img.getdata()), np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        width, height = img.size
        if img.mode == "RGB":
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        elif img.mode == "RGBA":
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture_id
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None


def init_textures():
    """Initialize all game textures"""
    global textures
    textures = {
        "desert_platform": load_texture("textures/desert_sand.jpg"),
        "ice_platform": load_texture("textures/ice_surface.jpg"),
        "forest_platform": load_texture("textures/forest_grass.jpg"),
        "coin": load_texture("textures/coin.png"),
        "portal": load_texture("textures/portal.png"),
        "player": load_texture("textures/player.png"),
    }


def init():
    """Initialize OpenGL settings"""
    glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Initialize lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Light position and properties
    light_position = [5.0, 10.0, 5.0, 1.0]
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Initialize game textures
    init_textures()

    # Initialize game objects
    reset_game()


def get_world_color():
    """Return the current world's primary color"""
    if current_world == WORLD_DESERT:
        return desert_color
    elif current_world == WORLD_ICE:
        return ice_color
    else:
        return forest_color


def get_platform_texture():
    """Return the appropriate texture for the current world"""
    if current_world == WORLD_DESERT:
        return textures["desert_platform"]
    elif current_world == WORLD_ICE:
        return textures["ice_platform"]
    else:
        return textures["forest_platform"]


def generate_platforms(count=10):
    """Generate initial set of platforms"""
    global platforms, last_platform_z

    platforms = []
    z_pos = last_platform_z
    width = 3.0

    for i in range(count):
        # Randomize x position for some platforms to create a winding path
        x_offset = 0
        if i > 2:  # Start randomizing after the first few platforms
            x_offset = random.uniform(-2, 2)

        # Create gaps occasionally
        gap = 0
        if i > 3 and random.random() < 0.3:  # 30% chance for a gap after the first few platforms
            gap = random.uniform(1.0, 2.0)

        # Platform length varies
        length = random.uniform(5.0, 10.0)

        platforms.append({
            'x': x_offset,
            'y': 0,
            'z': z_pos,
            'width': width,
            'length': length
        })

        # Update position for next platform
        z_pos -= (length + gap)
        last_platform_z = z_pos

    # Generate coins on platforms
    generate_coins()

    # Add a portal on one of the platforms
    add_portal()


def generate_coins():
    """Generate coins on platforms"""
    global coins
    coins = []

    on_platform = False
    for platform in platforms:
        if (player_z >= platform['z'] - platform['length'] and
                player_z <= platform['z'] and
                player_x >= platform['x'] - platform['width'] / 2 and
                player_x <= platform['x'] + platform['width'] / 2):
            # Player is above a platform
            if not is_jumping and jump_height <= 0.1:  # Player is on or very close to platform surface
                on_platform = True
                break
            elif is_jumping or jump_height > 0.1:  # Player is jumping, don't check for falling
                on_platform = True
                break



def add_portal():
    """Add a portal at the end of the path"""
    global portals

    # Find the last platform
    if platforms:
        last_platform = min(platforms, key=lambda p: p['z'])
        portals = [{
            'x': last_platform['x'],
            'y': 1.0,  # Height above platform
            'z': last_platform['z'] + last_platform['length'] / 2,
            'rotation': 0,
            'scale': 1.0
        }]


def reset_game():
    """Reset the game state for a new game"""
    global player_x, player_y, player_z, score, game_state, current_world
    global platforms, coins, portals, jump_height, is_jumping, last_platform_z

    player_x = 0
    player_y = 0.5
    player_z = -5
    jump_height = 0
    is_jumping = False
    score = 0
    game_state = STATE_PLAYING
    last_platform_z = -5

    # Initialize game objects
    generate_platforms()


def draw_textured_cube(texture_id, size=1.0):
    """Draw a textured cube centered at the origin"""
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Define the vertices of a cube
    vertices = [
        # Front face
        [-size, -size, size],
        [size, -size, size],
        [size, size, size],
        [-size, size, size],
        # Back face
        [-size, -size, -size],
        [-size, size, -size],
        [size, size, -size],
        [size, -size, -size],
        # Top face
        [-size, size, -size],
        [-size, size, size],
        [size, size, size],
        [size, size, -size],
        # Bottom face
        [-size, -size, -size],
        [size, -size, -size],
        [size, -size, size],
        [-size, -size, size],
        # Right face
        [size, -size, -size],
        [size, size, -size],
        [size, size, size],
        [size, -size, size],
        # Left face
        [-size, -size, -size],
        [-size, -size, size],
        [-size, size, size],
        [-size, size, -size]
    ]

    # Define texture coordinates
    tex_coords = [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ]

    # Draw the textured cube
    glBegin(GL_QUADS)
    for face in range(6):
        for i in range(4):
            glTexCoord2f(tex_coords[i][0], tex_coords[i][1])
            glVertex3f(vertices[face * 4 + i][0], vertices[face * 4 + i][1], vertices[face * 4 + i][2])
    glEnd()


def draw_textured_platform(x, y, z, width, length, texture_id):
    """Draw a textured platform"""
    glPushMatrix()
    glTranslatef(x, y, z)

    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Scale factor for texture repetition
    tex_scale_x = width / 2.0
    tex_scale_z = length / 2.0

    glBegin(GL_QUADS)
    # Top face
    glNormal3f(0, 1, 0)
    glTexCoord2f(0, 0)
    glVertex3f(-width / 2, 0, 0)
    glTexCoord2f(tex_scale_x, 0)
    glVertex3f(width / 2, 0, 0)
    glTexCoord2f(tex_scale_x, tex_scale_z)
    glVertex3f(width / 2, 0, -length)
    glTexCoord2f(0, tex_scale_z)
    glVertex3f(-width / 2, 0, -length)

    # Front face
    glNormal3f(0, 0, 1)
    glTexCoord2f(0, 0)
    glVertex3f(-width / 2, -0.5, 0)
    glTexCoord2f(tex_scale_x, 0)
    glVertex3f(width / 2, -0.5, 0)
    glTexCoord2f(tex_scale_x, 0.5)
    glVertex3f(width / 2, 0, 0)
    glTexCoord2f(0, 0.5)
    glVertex3f(-width / 2, 0, 0)

    # Side faces
    glNormal3f(1, 0, 0)
    glTexCoord2f(0, 0)
    glVertex3f(width / 2, -0.5, 0)
    glTexCoord2f(tex_scale_z, 0)
    glVertex3f(width / 2, -0.5, -length)
    glTexCoord2f(tex_scale_z, 0.5)
    glVertex3f(width / 2, 0, -length)
    glTexCoord2f(0, 0.5)
    glVertex3f(width / 2, 0, 0)

    glNormal3f(-1, 0, 0)
    glTexCoord2f(0, 0)
    glVertex3f(-width / 2, -0.5, -length)
    glTexCoord2f(tex_scale_z, 0)
    glVertex3f(-width / 2, -0.5, 0)
    glTexCoord2f(tex_scale_z, 0.5)
    glVertex3f(-width / 2, 0, 0)
    glTexCoord2f(0, 0.5)
    glVertex3f(-width / 2, 0, -length)

    # Back face
    glNormal3f(0, 0, -1)
    glTexCoord2f(0, 0)
    glVertex3f(width / 2, -0.5, -length)
    glTexCoord2f(tex_scale_x, 0)
    glVertex3f(-width / 2, -0.5, -length)
    glTexCoord2f(tex_scale_x, 0.5)
    glVertex3f(-width / 2, 0, -length)
    glTexCoord2f(0, 0.5)
    glVertex3f(width / 2, 0, -length)
    glEnd()

    glPopMatrix()


def draw_coin(x, y, z, rotation):
    """Draw a spinning coin"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)  # Rotate on Y-axis for spinning effect

    # Draw a flat, textured disc
    glBindTexture(GL_TEXTURE_2D, textures["coin"])

    glBegin(GL_QUADS)
    # Front face
    glNormal3f(0, 0, 1)
    glTexCoord2f(0, 0)
    glVertex3f(-0.3, -0.3, 0)
    glTexCoord2f(1, 0)
    glVertex3f(0.3, -0.3, 0)
    glTexCoord2f(1, 1)
    glVertex3f(0.3, 0.3, 0)
    glTexCoord2f(0, 1)
    glVertex3f(-0.3, 0.3, 0)

    # Back face (flipped texture)
    glNormal3f(0, 0, -1)
    glTexCoord2f(0, 0)
    glVertex3f(0.3, -0.3, 0)
    glTexCoord2f(1, 0)
    glVertex3f(-0.3, -0.3, 0)
    glTexCoord2f(1, 1)
    glVertex3f(-0.3, 0.3, 0)
    glTexCoord2f(0, 1)
    glVertex3f(0.3, 0.3, 0)
    glEnd()

    glPopMatrix()


def draw_portal(x, y, z, rotation, scale):
    """Draw a portal"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)  # Rotate on Y-axis

    # Use billboard technique to always face camera
    glBindTexture(GL_TEXTURE_2D, textures["portal"])

    # Draw a large textured quad
    size = 2.0 * scale
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glTexCoord2f(0, 0)
    glVertex3f(-size, -size, 0)
    glTexCoord2f(1, 0)
    glVertex3f(size, -size, 0)
    glTexCoord2f(1, 1)
    glVertex3f(size, size, 0)
    glTexCoord2f(0, 1)
    glVertex3f(-size, size, 0)
    glEnd()

    glPopMatrix()


def draw_player():
    """Draw the player character"""
    glPushMatrix()
    glTranslatef(player_x, player_y + jump_height, player_z)

    # Draw player cube
    draw_textured_cube(textures["player"], 0.4)

    glPopMatrix()


def draw_world():
    """Draw the current world's environment based on the world type"""
    world_color = get_world_color()
    platform_texture = get_platform_texture()

    # Set fog color based on world
    fog_color = [world_color[0] * 0.8, world_color[1] * 0.8, world_color[2] * 0.8, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)

    # Draw platforms
    for platform in platforms:
        draw_textured_platform(
            platform['x'], platform['y'], platform['z'],
            platform['width'], platform['length'],
            platform_texture
        )

    # Draw coins
    for coin in coins:
        if not coin['collected']:
            draw_coin(coin['x'], coin['y'], coin['z'], coin['rotation'])

    # Draw portals
    for portal in portals:
        draw_portal(
            portal['x'], portal['y'], portal['z'],
            portal['rotation'], portal['scale']
        )


def draw_score():
    """Draw the score on screen"""
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Switch to orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw score text
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2i(10, window_height - 20)
    score_text = f"Score: {score}"
    for c in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Draw high score
    glRasterPos2i(10, window_height - 40)
    high_score_text = f"High Score: {high_score}"
    for c in high_score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Restore previous matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_menu():
    """Draw the main menu"""
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Switch to orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw title
    glColor3f(1.0, 1.0, 0.0)  # Yellow color
    title = "PORTAL RUNNER"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in title)
    glRasterPos2i((window_width - string_width) // 2, window_height - 100)
    for c in title:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Draw instructions
    glColor3f(1.0, 1.0, 1.0)  # White color
    instructions = "Press SPACE to start"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in instructions)
    glRasterPos2i((window_width - string_width) // 2, window_height // 2)
    for c in instructions:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Controls instruction
    controls = "Use A/D to move left/right, W to jump"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in controls)
    glRasterPos2i((window_width - string_width) // 2, window_height // 2 - 30)
    for c in controls:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Restore previous matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_game_over():
    """Draw game over screen"""
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Switch to orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw game over text
    glColor3f(1.0, 0.0, 0.0)  # Red color
    text = "GAME OVER"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
    glRasterPos2i((window_width - string_width) // 2, window_height - 100)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Draw final score
    glColor3f(1.0, 1.0, 1.0)  # White color
    score_text = f"Final Score: {score}"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in score_text)
    glRasterPos2i((window_width - string_width) // 2, window_height // 2)
    for c in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Restart instruction
    restart_text = "Press SPACE to restart"
    string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in restart_text)
    glRasterPos2i((window_width - string_width) // 2, window_height // 2 - 30)
    for c in restart_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Restore previous matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


def draw_portal_transition():
    """Draw portal transition effect"""
    global transition_start_time, current_world, next_world

    # Calculate transition progress (0 to 1)
    current_time = time.time()
    progress = min(1.0, (current_time - transition_start_time) / transition_duration)

    # Draw swirling portal effect
    glDisable(GL_LIGHTING)

    # Switch to orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw portal transition effect (swirling circles)
    center_x = window_width / 2
    center_y = window_height / 2
    max_radius = window_width if window_width > window_height else window_height

    # Get color of the next world
    if next_world == WORLD_DESERT:
        color = desert_color
    elif next_world == WORLD_ICE:
        color = ice_color
    else:
        color = forest_color

    # Draw concentric circles with varying opacity
    for i in range(20):
        t = i / 19.0  # 0 to 1
        radius = max_radius * (1.0 - progress) * (1.0 - t)

        glPushMatrix()
        glTranslatef(center_x, center_y, 0)

        # Set color with opacity
        glColor4f(color[0], color[1], color[2], 0.1)

        # Draw circle
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)  # Center
        segments = 32
        for j in range(segments + 1):
            angle = 2.0 * math.pi * j / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()

        glPopMatrix()

    # Text indicating the new world
    if progress > 0.5:
        glColor3f(1.0, 1.0, 1.0)  # White color

        if next_world == WORLD_DESERT:
            text = "Entering Desert World"
        elif next_world == WORLD_ICE:
            text = "Entering Ice World"
        else:
            text = "Entering Forest World"

        string_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
        glRasterPos2i((window_width - string_width) // 2, window_height // 2)
        for c in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Restore previous matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glEnable(GL_LIGHTING)

    # If transition is complete, switch worlds
    if progress >= 1.0:
        current_world = next_world
        game_state = STATE_PLAYING
        reset_game()  # Generate new level in the new world


def display():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_GAME_OVER:
        draw_game_over()
    elif game_state == STATE_PORTAL_TRANSITION:
        draw_portal_transition()
    else:  # STATE_PLAYING
        # Set up 3D perspective projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, window_width / window_height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Position camera behind player
        gluLookAt(
            player_x, player_y + 1.5, player_z + 5,  # Eye position
            player_x, player_y, player_z - 5,  # Look at position
            0, 1, 0  # Up vector
        )

        # Draw the world and game objects
        draw_world()
        draw_player()
        draw_score()

    glutSwapBuffers()


def reshape(width, height):
    """Handle window resizing"""
    global window_width, window_height

    window_width = width
    window_height = height

    glViewport(0, 0, width, height)

    # Set up projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)


def update_objects():
    """Update game objects"""
    global score, high_score, game_state, jump_height, is_jumping
    global player_z, transition_start_time, next_world

    # Update jump animation
    if is_jumping:
        jump_height += 0.1
        if jump_height >= 1.0:
            is_jumping = False
    elif jump_height > 0:
        jump_height -= 0.1
        if jump_height < 0:
            jump_height = 0

    # Move player forward
    player_z -= platform_speed

    # Rotate coins
    for coin in coins:
        coin['rotation'] = (coin['rotation'] + 5) % 360

    # Rotate portals
    for portal in portals:
        portal['rotation'] = (portal['rotation'] + 1) % 360

        # Make portal "breathe" by changing scale
        portal['scale'] = 1.0 + 0.1 * math.sin(time.time() * 2)

        # Check if player has fallen off
    on_platform = False
    for platform in platforms:
        # Check if player is horizontally above a platform
        if (player_z >= platform['z'] - platform['length'] and
                player_z <= platform['z'] and
                player_x >= platform['x'] - platform['width'] / 2 and
                player_x <= platform['x'] + platform['width'] / 2):
            # We're above a platform horizontally, now check vertical position
            if jump_height <= 0.6:  # Player is on or close to platform surface, or currently jumping
                on_platform = True
            break
    if not on_platform and jump_height < 0.3:
        game_state = STATE_GAME_OVER
        if score > high_score:
            high_score = score

    # Check for coin collection
    for coin in coins:
        if not coin['collected']:
            # Calculate distance between player and coin
            dx = player_x - coin['x']
            dz = player_z - coin['z']
            dy = (player_y + jump_height) - coin['y']
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            # If player is close enough, collect the coin
            if distance < 0.7:
                coin['collected'] = True
                score += 10

    # Check for portal interaction
    for portal in portals:
        # Calculate distance between player and portal
        dx = player_x - portal['x']
        dz = player_z - portal['z']
        distance = math.sqrt(dx * dx + dz * dz)

        # If player is close enough, activate portal
        if distance < 1.5:
            # Start portal transition
            game_state = STATE_PORTAL_TRANSITION
            transition_start_time = time.time()

            # Choose next world (different from current)
            next_world = random.choice([w for w in [WORLD_DESERT, WORLD_ICE, WORLD_FOREST] if w != current_world])

    # Check if we need to generate more platforms
    if len(platforms) < 5:
        generate_platforms(10)


def keyboard(key, x, y):
    """Handle keyboard input"""
    global player_x, is_jumping, game_state

    key = key.decode('utf-8').lower() if isinstance(key, bytes) else chr(key).lower()

    if game_state == STATE_PLAYING:
        # Player movement
        if key == 'a':
            player_x -= player_speed
        elif key == 'd':
            player_x += player_speed
        elif key == 'w' and not is_jumping and jump_height == 0:
            is_jumping = True

        # Limit player movement to not fall off the sides
        player_x = max(-4, min(4, player_x))

    elif game_state == STATE_MENU or game_state == STATE_GAME_OVER:
        # Start/restart game on space bar
        if key == ' ':
            reset_game()

    # Quit game on escape
    if key == chr(27):  # ESC key
        sys.exit(0)


def special_keys(key, x, y):
    """Handle special key input (arrow keys)"""
    global player_x, is_jumping

    if game_state == STATE_PLAYING:
        # Alternative controls using arrow keys
        if key == GLUT_KEY_LEFT:
            player_x -= player_speed
        elif key == GLUT_KEY_RIGHT:
            player_x += player_speed
        elif key == GLUT_KEY_UP and not is_jumping and jump_height == 0:
            is_jumping = True

        # Limit player movement to not fall off the sides
        player_x = max(-4, min(4, player_x))


def idle():
    """Idle function for animation"""
    if game_state == STATE_PLAYING:
        update_objects()

    # Force redisplay
    glutPostRedisplay()


def main():
    """Main function to initialize and start the game"""
    # Initialize GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Portal Runner")

    # Set up callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutIdleFunc(idle)

    # Initialize OpenGL
    init()

    # Start main loop
    glutMainLoop()


if __name__ == "__main__":
    main()