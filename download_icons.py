"""
Download custom icons for the FR4 Leaking Tool GUI
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_icon_from_emoji(emoji, size=(64, 64), filename="icon.png"):
    """Create an icon from emoji text"""
    # Create a new image with transparent background
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a font that supports emojis
    try:
        # Windows has Segoe UI Emoji
        font = ImageFont.truetype("seguiemj.ttf", int(size[0] * 0.7))
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(size[0] * 0.7))
        except:
            font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size[0] - text_width) / 2 - bbox[0]
    y = (size[1] - text_height) / 2 - bbox[1]
    
    draw.text((x, y), emoji, font=font, fill=(255, 255, 255, 255))
    
    # Save the icon
    img.save(os.path.join('assets', filename))
    print(f"Created: {filename}")

def download_fun_run_icon():
    """Try to download Fun Run 4 icon"""
    # Fun Run 4 icon URLs (trying multiple sources)
    urls = [
        "https://play-lh.googleusercontent.com/6hPsuaM_oN0hW8B1LzZLqF5CQN5cEv8fZ0ov8xLlvQCvKUqRhR4jP5jVxQxNFJQYfQ=w240-h480",
        "https://is1-ssl.mzstatic.com/image/thumb/Purple126/v4/3f/8e/0e/3f8e0e8a-0e8e-0e8e-0e8e-0e8e0e8e0e8e/AppIcon-0-0-1x_U007emarketing-0-0-0-7-0-0-sRGB-0-0-0-GLES2_U002c0-512MB-85-220-0-0.png/230x0w.webp"
    ]
    
    for i, url in enumerate(urls):
        try:
            print(f"Attempting to download Fun Run 4 icon from source {i+1}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                # Resize to standard sizes
                img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
                img_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
                img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
                
                img_64.save(os.path.join('assets', 'logo_64.png'))
                img_128.save(os.path.join('assets', 'logo_128.png'))
                img_256.save(os.path.join('assets', 'logo_256.png'))
                
                print("✓ Successfully downloaded Fun Run 4 logo!")
                return True
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    print("⚠ Could not download Fun Run 4 icon from web")
    print("  Creating placeholder logo...")
    create_placeholder_logo()
    return False

def create_placeholder_logo():
    """Create a placeholder logo with FR4 text"""
    sizes = [(64, 64), (128, 128), (256, 256)]
    
    for size in sizes:
        # Create colorful gradient background
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a circle background (game-like)
        circle_color = (66, 135, 245, 255)  # Nice blue
        draw.ellipse([0, 0, size[0], size[1]], fill=circle_color)
        
        # Draw "FR4" text
        try:
            font = ImageFont.truetype("arial.ttf", int(size[0] * 0.35))
        except:
            font = ImageFont.load_default()
        
        text = "FR4"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) / 2 - bbox[0]
        y = (size[1] - text_height) / 2 - bbox[1]
        
        # Draw text with shadow
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        filename = f"logo_{size[0]}.png"
        img.save(os.path.join('assets', filename))
        print(f"Created placeholder: {filename}")

def create_custom_icons():
    """Create custom icons for different actions"""
    
    icons = {
        # Navigation icons
        'monitor.png': '📡',
        'compare.png': '🔍',
        'modify.png': '🔧',
        'logs.png': '📋',
        
        # Action icons
        'check.png': '✓',
        'search.png': '🔎',
        'settings.png': '⚙️',
        'refresh.png': '🔄',
        'delete.png': '🗑️',
        'alert.png': '🚨',
        'info.png': 'ℹ️',
        'warning.png': '⚠️',
        'folder.png': '📁',
        'file.png': '📄',
        'save.png': '💾',
        'download.png': '📥',
        'upload.png': '📤',
    }
    
    print("\nCreating custom icons...")
    for filename, emoji in icons.items():
        create_icon_from_emoji(emoji, (48, 48), filename)
    
    print("\n✓ All icons created successfully!")

def create_button_icons():
    """Create larger icons for buttons"""
    
    button_icons = {
        'btn_check.png': ('🔍', (40, 40)),
        'btn_play.png': ('▶️', (40, 40)),
        'btn_pause.png': ('⏸️', (40, 40)),
        'btn_reset.png': ('🔄', (40, 40)),
        'btn_compare.png': ('🔍', (40, 40)),
        'btn_modify.png': ('🔧', (40, 40)),
    }
    
    print("\nCreating button icons...")
    for filename, (emoji, size) in button_icons.items():
        create_icon_from_emoji(emoji, size, filename)
    
    print("✓ Button icons created!")

def main():
    print("="*60)
    print("FR4 Leaking Tool - Icon Generator")
    print("="*60)
    print()
    
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
        print("Created 'assets' directory")
    
    # Try to download Fun Run 4 logo
    print("\n1. Downloading Fun Run 4 Logo...")
    print("-" * 60)
    download_fun_run_icon()
    
    # Create custom icons
    print("\n2. Creating Custom Icons...")
    print("-" * 60)
    create_custom_icons()
    
    # Create button icons
    print("\n3. Creating Button Icons...")
    print("-" * 60)
    create_button_icons()
    
    print("\n" + "="*60)
    print("✓ Icon generation complete!")
    print("="*60)
    print("\nAll icons saved to 'assets' folder")
    print("\nYou can now run the GUI application.")

if __name__ == "__main__":
    main()
