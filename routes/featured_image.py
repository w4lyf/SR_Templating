from flask import Blueprint, request, jsonify
from services.image_utils import compress_image, save_compressed_image
import requests
import os
import tempfile
import logging
import re

featured_bp = Blueprint('featured', __name__)

# Setup logger for this blueprint
logger = logging.getLogger('featured')
logger.setLevel(logging.DEBUG)  # Adjust as needed
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@featured_bp.route('/process_featured', methods=['POST'])
def process_featured():
    try:
        logger.info("🔧 Starting featured image processing...")
        data = request.get_json(force=True)
        featured_url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        game_name = data.get('game_name', '').strip()

        if not featured_url:
            logger.warning("❌ No featured image URL provided.")
            return jsonify({'error': 'Featured image URL is required'}), 400
        if not api_key:
            logger.warning("❌ No MagicAPI key provided.")
            return jsonify({'error': 'MagicAPI key is required'}), 400

        # Send request to MagicAPI
        upscale_endpoint = "https://api.magicapi.dev/api/v1/magicapi/upscaler/upscale2x/"
        headers = {
            "accept": "image/jpeg",
            "x-magicapi-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {"url": featured_url}

        logger.info(f"📤 Sending image to MagicAPI for upscaling...")
        response = requests.post(upscale_endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        logger.info("✅ Received response from MagicAPI.")

        # Validate content type
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/jpeg"):
            logger.error(f"❌ Unexpected content-type: {content_type}")
            return jsonify({'error': 'Unexpected response from MagicAPI'}), 502

        # Save the upscaled image to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name
        logger.info(f"📁 Saved upscaled image temporarily at: {temp_path}")

        game_name = sanitize_filename(game_name)

        try:
            # Compress the image
            compressed_data = compress_image(temp_path, max_size_kb=50)
            logger.info("📦 Compressed image successfully.")

            # Save compressed image to final destination
            filename = f"{game_name}_featured_final.jpg"
            filepath = save_compressed_image(compressed_data, filename)
            logger.info(f"💾 Saved compressed image at: {filepath}")

            return jsonify({
                'success': True,
                'message': 'Image upscaled and compressed successfully',
                'local_path': filepath,
                'original_url': featured_url,
                'size_kb': round(len(compressed_data) / 1024, 2)
            })

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"🧹 Deleted temporary file: {temp_path}")

    except requests.exceptions.RequestException as req_err:
        logger.exception("🔌 Error communicating with MagicAPI.")
        return jsonify({'error': f'Error connecting to MagicAPI: {str(req_err)}'}), 502

    except Exception as e:
        logger.exception("💥 General failure in image processing.")
        return jsonify({'error': f'Failed to process featured image: {str(e)}'}), 500
    
def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "", name)
