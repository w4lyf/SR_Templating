from PIL import Image
import io
import os
import requests

def compress_image(image_input, max_size_kb=50, quality=85):
    print("im in compress_image")
    """Compress image from file path, URL, or PIL.Image.Image"""
    try:
        # Handle PIL image directly
        if isinstance(image_input, Image.Image):
            img = image_input
            print("compressing provided PIL image")
        elif os.path.exists(image_input):
            with open(image_input, 'rb') as f:
                img = Image.open(f)
                img.load()
                print("loaded image from local path")
        else:
            response = requests.get(image_input, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            print("downloaded image from url")

        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        print("converted image to RGB")

        for q in range(quality, 10, -5):
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=q, optimize=True)
            if len(buffer.getvalue()) <= max_size_kb * 1024:
                print(f"compressed at quality {q}")
                return buffer.getvalue()

        img.thumbnail((800, 600), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=70, optimize=True)
        print("resized image to fit within max size")
        return buffer.getvalue()

    except Exception as e:
        raise Exception(f"Failed to compress image: {str(e)}")

def save_compressed_image(image_data, filename):
    print("im in save_compressed_image")
    """Save compressed image data to file"""
    os.makedirs('static/images', exist_ok=True)
    filepath = f'static/images/{filename}'
    with open(filepath, 'wb') as f:
        f.write(image_data)
    return filepath