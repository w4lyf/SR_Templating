from flask import Blueprint, request, jsonify
from PIL import Image
import requests
import re
from io import BytesIO
import os

from services.image_utils import compress_image, save_compressed_image

thumbnail_bp = Blueprint('thumbnail', __name__)

@thumbnail_bp.route('/process_thumbnail', methods=['POST'])
def handle_process_thumbnail():
    print("i made it here")
    try:
        data = request.get_json()
        thumbnail_url = data.get('url', '').strip()
        game_name = data.get('game_name', '').strip()
        print(f"Received thumbnail URL: {thumbnail_url} and game name: {game_name}")

        if not thumbnail_url:
            return jsonify({'error': 'Thumbnail URL is required'}), 400
        if not game_name:
            return jsonify({'error': 'Game name is required'}), 400
        print("got past the checks")

        filepath, compressed_data = process_thumbnail(thumbnail_url, game_name)
        print(f"Processed thumbnail saved at: {filepath}")

        return jsonify({
            'success': True,
            'message': 'Thumbnail processed successfully',
            'image_url': f"http://localhost:5000/images/{os.path.basename(filepath)}",
            'size_kb': len(compressed_data) / 1024
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process thumbnail: {str(e)}'}), 500

def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "", name)

def download_image(url, size):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    return img.resize(size, Image.LANCZOS)

def process_thumbnail(thumbnail_url, game_name, overlay_path="poster.png"):
    print("im in process_thumbnail")
    game_name = sanitize_filename(game_name)
    print("new game_name:", game_name)
    img = download_image(thumbnail_url, (584, 800))
    print("downloaded image")

    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        img_rgba = img.convert("RGBA")
        img_rgba.paste(overlay, (0, 0), overlay)
        img = img_rgba.convert("RGB")
    except Exception:
        # Overlay failed (file missing or incompatible), continue without overlay
        pass

    compressed_data = compress_image(img, max_size_kb=50)
    #print(compressed_data)
    filename = f"{game_name}_thumbnail_final.jpg"
    filepath = save_compressed_image(compressed_data, filename)
    return filepath, compressed_data