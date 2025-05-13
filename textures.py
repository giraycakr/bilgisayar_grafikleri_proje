#!/usr/bin/env python3
"""
Texture loading and management for Portal Runner
"""

import os
import numpy as np
from PIL import Image
from OpenGL.GL import *


class TextureManager:
    def __init__(self):
        self.textures = {}

    def load_texture(self, filepath):
        """Load a texture from file and return its OpenGL ID"""
        try:
            img = Image.open(filepath)
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
            print(f"Error loading texture {filepath}: {e}")
            return None

    def init_all_textures(self):
        """Initialize all game textures"""
        texture_files = {
            "desert_platform": "textures/desert_sand.jpg",
            "ice_platform": "textures/ice_surface.jpg",
            "forest_platform": "textures/forest_grass.jpg",
            "coin": "textures/coin.png",
            "portal": "textures/portal.png",
            "player": "textures/player.png",
        }

        for name, filepath in texture_files.items():
            texture_id = self.load_texture(filepath)
            if texture_id:
                self.textures[name] = texture_id
            else:
                print(f"Warning: Could not load texture {name}")
                # Create a fallback texture
                self.textures[name] = self.create_fallback_texture()

    def create_fallback_texture(self):
        """Create a simple fallback texture when loading fails"""
        # Create a 2x2 checkerboard pattern
        texture_data = np.array([
            [255, 0, 255, 255], [0, 255, 0, 255],
            [0, 255, 0, 255], [255, 0, 255, 255]
        ], dtype=np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        return texture_id

    def get_texture(self, name):
        """Get a texture by name"""
        return self.textures.get(name)

    def bind_texture(self, name):
        """Bind a texture for use"""
        texture_id = self.get_texture(name)
        if texture_id:
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            print(f"Warning: Texture '{name}' not found")