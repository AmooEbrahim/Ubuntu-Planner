#!/usr/bin/env python3
"""Generate simple icon images for tray icon."""
from PIL import Image, ImageDraw
from pathlib import Path


def create_icon(color, filename, size=22):
    """Create a simple circular icon.

    Args:
        color: RGB tuple for the icon color
        filename: Output filename
        size: Icon size in pixels
    """
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw circle
    margin = 2
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=color,
        outline=(255, 255, 255, 255),
        width=1
    )

    # Save
    img.save(filename)
    print(f"Created: {filename}")


def main():
    """Generate all icon variations."""
    assets_dir = Path(__file__).parent / 'assets'
    assets_dir.mkdir(exist_ok=True)

    # Icon colors
    icons = {
        'icon-idle.png': (128, 128, 128, 255),      # Gray
        'icon-active.png': (34, 197, 94, 255),      # Green
        'icon-overtime.png': (249, 115, 22, 255),   # Orange
    }

    for filename, color in icons.items():
        create_icon(color, assets_dir / filename)

    print("\nAll icons generated successfully!")


if __name__ == '__main__':
    main()
