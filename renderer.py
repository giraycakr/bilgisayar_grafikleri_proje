#!/usr/bin/env python3
"""
Rendering functions for Portal Runner
"""

import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from constants import *


class Renderer:
    def __init__(self, texture_manager):
        self.texture_manager = texture_manager

        # Fix for bitmap font constants - use the module reference
        try:
            self.font_large = OpenGL.GLUT.GLUT_BITMAP_HELVETICA_18
            self.font_medium = OpenGL.GLUT.GLUT_BITMAP_HELVETICA_12
        except AttributeError:
            # Fallback if the constants aren't available
            self.font_large = b'\x12'  # Placeholder
            self.font_medium = b'\x0c'  # Placeholder

    def init_gl(self):
        """Initialize OpenGL settings"""
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Initialize lighting with more robust setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Light position and properties (more stable lighting)
        light_position = [5.0, 10.0, 5.0, 1.0]
        light_ambient = [0.4, 0.4, 0.4, 1.0]  # Increased ambient
        light_diffuse = [0.8, 0.8, 0.8, 1.0]  # Reduced diffuse for more stable lighting
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # Set model lighting parameters for more stable appearance
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_FALSE)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])

        # Ensure proper default color
        glColor3f(1.0, 1.0, 1.0)

    def setup_3d_projection(self, width, height):
        """Set up 3D perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def setup_2d_projection(self, width, height):
        """Set up 2D orthographic projection for UI"""
        # Save current OpenGL state including lighting
        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_LIGHTING_BIT)

        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)  # Disable depth testing for UI

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def restore_3d_projection(self):
        """Restore 3D projection after 2D rendering"""
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # Restore all OpenGL state including lighting
        glPopAttrib()

        # Ensure proper lighting state is restored
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)

        # Reset color to white and ensure proper color material
        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    def draw_text(self, x, y, text, font=None):
        """Draw text at given position"""
        if font is None:
            font = self.font_large

        glRasterPos2i(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))

    def get_text_width(self, text, font=None):
        """Calculate text width for centering"""
        if font is None:
            font = self.font_large
        return sum(glutBitmapWidth(font, ord(c)) for c in text)

    def draw_centered_text(self, y, text, width, font=None):
        """Draw centered text"""
        text_width = self.get_text_width(text, font)
        x = (width - text_width) // 2
        self.draw_text(x, y, text, font)

    def draw_platform(self, platform, texture_name):
        """Draw a textured platform"""
        glPushMatrix()
        glTranslatef(platform['x'], platform['y'], platform['z'])

        self.texture_manager.bind_texture(texture_name)

        # Scale factor for texture repetition
        width = platform['width']
        length = platform['length']
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

        # Draw sides
        self._draw_platform_sides(width, length, tex_scale_x, tex_scale_z)
        glEnd()

        glPopMatrix()

    def _draw_platform_sides(self, width, length, tex_scale_x, tex_scale_z):
        """Draw the sides of a platform"""
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

        # Right side
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0)
        glVertex3f(width / 2, -0.5, 0)
        glTexCoord2f(tex_scale_z, 0)
        glVertex3f(width / 2, -0.5, -length)
        glTexCoord2f(tex_scale_z, 0.5)
        glVertex3f(width / 2, 0, -length)
        glTexCoord2f(0, 0.5)
        glVertex3f(width / 2, 0, 0)

        # Left side
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

    def draw_coin(self, coin):
        """Draw a spinning coin"""
        glPushMatrix()
        glTranslatef(coin['x'], coin['y'], coin['z'])
        glRotatef(coin['rotation'], 0, 1, 0)

        self.texture_manager.bind_texture("coin")

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

        # Back face
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

    def draw_portal(self, portal):
        """Draw a portal"""
        glPushMatrix()
        glTranslatef(portal['x'], portal['y'], portal['z'])
        glRotatef(portal['rotation'], 0, 1, 0)

        self.texture_manager.bind_texture("portal")

        size = 2.0 * portal['scale']
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

    def draw_player(self, player):
        """Draw the player character"""
        # Ensure proper color state
        glColor3f(1.0, 1.0, 1.0)

        pos = player.get_position()
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])

        self.texture_manager.bind_texture("player")
        self.draw_textured_cube(0.4)

        glPopMatrix()

    def draw_textured_cube(self, size=1.0):
        """Draw a textured cube centered at the origin"""
        # Ensure normal vectors are properly set for lighting
        glEnable(GL_NORMALIZE)  # Normalize normals for proper lighting

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

        # Define normals for each face
        normals = [
            [0, 0, 1],  # Front
            [0, 0, -1],  # Back
            [0, 1, 0],  # Top
            [0, -1, 0],  # Bottom
            [1, 0, 0],  # Right
            [-1, 0, 0]  # Left
        ]

        # Draw the textured cube with proper normals
        glBegin(GL_QUADS)
        for face in range(6):
            glNormal3f(normals[face][0], normals[face][1], normals[face][2])
            for i in range(4):
                glTexCoord2f(tex_coords[i][0], tex_coords[i][1])
                glVertex3f(vertices[face * 4 + i][0], vertices[face * 4 + i][1], vertices[face * 4 + i][2])
        glEnd()

    def draw_portal_transition(self, progress, next_world, width, height):
        """Draw portal transition effect"""
        self.setup_2d_projection(width, height)

        # Draw swirling portal effect
        center_x = width / 2
        center_y = height / 2
        max_radius = width if width > height else height

        # Get color of the next world
        color = WORLD_COLORS[next_world]

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

            if next_world == WorldType.DESERT:
                text = "Entering Desert World"
            elif next_world == WorldType.ICE:
                text = "Entering Ice World"
            else:
                text = "Entering Forest World"

            self.draw_centered_text(height // 2, text, width)

        self.restore_3d_projection()

    def draw_world(self, world_manager, player):
        """Draw the entire world"""
        # Set fog color based on world
        world_color = world_manager.get_world_color()
        fog_color = [world_color[0] * 0.8, world_color[1] * 0.8, world_color[2] * 0.8, 1.0]
        glFogfv(GL_FOG_COLOR, fog_color)

        # Reset color to white for 3D rendering
        glColor3f(1.0, 1.0, 1.0)

        texture_name = world_manager.get_world_texture_name()

        # Draw chunks that are near the player (increased range)
        player_z = player.z
        for chunk in world_manager.platform_chunks:
            # Show chunks within a larger range (was -50 to +20, now -100 to +50)
            if chunk.start_z > player_z + 50 or chunk.start_z < player_z - 100:
                continue

            # Draw platforms
            for platform in chunk.platforms:
                glColor3f(1.0, 1.0, 1.0)  # Ensure white color for each platform
                self.draw_platform(platform, texture_name)

            # Draw coins
            for coin in chunk.coins:
                if not coin['collected']:
                    glColor3f(1.0, 1.0, 1.0)  # Ensure white color for each coin
                    self.draw_coin(coin)

            # Draw portals
            for portal in chunk.portals:
                glColor3f(1.0, 1.0, 1.0)  # Ensure white color for each portal
                self.draw_portal(portal)