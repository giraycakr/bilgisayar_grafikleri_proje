#!/usr/bin/env python3
"""
Setup script to create the textures directory and generate placeholder textures.
This is helpful for getting started with the Portal Runner game.
"""

import os
import sys
from PIL import Image, ImageDraw


def create_texture_dir():
    """Create the textures directory if it doesn't exist"""
    if not os.path.exists('textures'):
        os.makedirs('textures')
        print("Created 'textures' directory")
    else:
        print("'textures' directory already exists")


def create_color_texture(filename, color, size=(256, 256)):
    """Create a simple colored texture with a pattern"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    # Add some pattern
    for i in range(0, size[0], 32):
        for j in range(0, size[1], 32):
            if (i + j) % 64 == 0:
                # Draw a darker square
                darker_color = tuple(max(0, c - 30) for c in color)
                draw.rectangle([i, j, i + 16, j + 16], fill=darker_color)

    # Save the texture
    path = os.path.join('textures', filename)
    img.save(path)
    print(f"Created texture: {path}")


def create_coin_texture():
    """Create a simple coin texture"""
    size = (128, 128)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw golden circle
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 2 - 10
    draw.ellipse([center[0] - radius, center[1] - radius,
                  center[0] + radius, center[1] + radius],
                 fill=(255, 215, 0, 255))

    # Draw inner details
    inner_radius = radius * 0.7
    draw.ellipse([center[0] - inner_radius, center[1] - inner_radius,
                  center[0] + inner_radius, center[1] + inner_radius],
                 fill=(255, 235, 59, 255))

    # Add a dollar sign
    draw.text((center[0] - 10, center[1] - 15), "$", fill=(255, 140, 0, 255), font_size=30)

    # Save the texture
    path = os.path.join('textures', 'coin.png')
    img.save(path)
    print(f"Created texture: {path}")


def create_portal_texture():
    """Create a simple portal texture"""
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw concentric circles with different colors
    center = (size[0] // 2, size[1] // 2)
    colors = [
        (75, 0, 130, 220),  # Indigo
        (138, 43, 226, 200),  # BlueViolet
        (148, 0, 211, 180),  # DarkViolet
        (186, 85, 211, 160),  # MediumOrchid
        (218, 112, 214, 140)  # Orchid
    ]

    max_radius = min(size) // 2 - 10
    for i, color in enumerate(colors):
        radius = max_radius * (1 - i * 0.2)
        draw.ellipse([center[0] - radius, center[1] - radius,
                      center[0] + radius, center[1] + radius],
                     fill=color)

    # Save the texture
    path = os.path.join('textures', 'portal.png')
    img.save(path)
    print(f"Created texture: {path}")


def create_player_texture():
    """Create a simple player texture"""
    size = (128, 128)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fill background with blue
    draw.rectangle([0, 0, size[0], size[1]], fill=(30, 144, 255, 255))

    # Add details
    # Face
    draw.rectangle([size[0] // 4, size[1] // 4, 3 * size[0] // 4, 3 * size[1] // 4],
                   fill=(255, 222, 173, 255))

    # Eyes
    eye_size = size[0] // 10
    draw.ellipse([size[0] // 3 - eye_size // 2, size[1] // 3 - eye_size // 2,
                  size[0] // 3 + eye_size // 2, size[1] // 3 + eye_size // 2],
                 fill=(0, 0, 0, 255))
    draw.ellipse([2 * size[0] // 3 - eye_size // 2, size[1] // 3 - eye_size // 2,
                  2 * size[0] // 3 + eye_size // 2, size[1] // 3 + eye_size // 2],
                 fill=(0, 0, 0, 255))

    # Mouth
    draw.arc([size[0] // 3, size[1] // 2, 2 * size[0] // 3, 2 * size[1] // 3],
             start=0, end=180, fill=(0, 0, 0, 255), width=2)

    # Save the texture
    path = os.path.join('textures', 'player.png')
    img.save(path)
    print(f"Created texture: {path}")


def main():
    """Main function to set up all textures"""
    create_texture_dir()

    # Create basic terrain textures
    create_color_texture('desert_sand.jpg', (239, 221, 111))  # Sandy yellow
    create_color_texture('ice_surface.jpg', (173, 216, 230))  # Light blue
    create_color_texture('forest_grass.jpg', (34, 139, 34))  # Forest green

    # Create object textures
    create_coin_texture()
    create_portal_texture()
    create_player_texture()

    print("\nAll textures have been created!")
    print("You can now run the game using: python portal_runner.py")


if __name__ == "__main__":
    main()