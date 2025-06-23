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
            logger.warning("❌ No Picsart API key provided.")
            return jsonify({'error': 'Picsart API key is required'}), 400

        # Prepare request to Picsart API
        logger.info(f"📤 Sending image to Picsart API for upscaling...")

        url = "https://api.picsart.io/tools/1.0/upscale"
        boundary = "---011000010111000001101001"
        payload = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"upscale_factor\"\r\n\r\n2\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"format\"\r\n\r\nJPG\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"image_url\"\r\n\r\n{featured_url}\r\n"
            f"--{boundary}--"
        )

        headers = {
            "accept": "application/json",
            "content-type": f"multipart/form-data; boundary={boundary}",
            "X-Picsart-API-Key": api_key
        }

        response = requests.post(url, headers=headers, data=payload.encode('utf-8'), timeout=120)
        response.raise_for_status()
        logger.info("✅ Received response from Picsart API.")

        result = response.json()
        if result.get("status") != "success" or not result.get("data", {}).get("url"):
            logger.error("❌ Invalid response from Picsart API.")
            return jsonify({'error': 'Unexpected response from Picsart API'}), 502

        upscaled_url = result["data"]["url"]
        logger.info(f"📎 Upscaled image URL: {upscaled_url}")

        # Download the upscaled image
        upscaled_response = requests.get(upscaled_url, timeout=60)
        upscaled_response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(upscaled_response.content)
            temp_path = tmp_file.name
        logger.info(f"📁 Saved upscaled image temporarily at: {temp_path}")

        game_name = sanitize_filename(game_name)

        try:
            compressed_data = compress_image(temp_path, max_size_kb=50)
            logger.info("📦 Compressed image successfully.")

            filename = f"{game_name}_featured_final.jpg"
            filepath = save_compressed_image(compressed_data, filename)
            logger.info(f"💾 Saved compressed image at: {filepath}")

            return jsonify({
                'success': True,
                'message': 'Image upscaled and compressed successfully',
                'local_path': filepath,
                'original_url': featured_url,
                'upscaled_url': upscaled_url,
                'size_kb': round(len(compressed_data) / 1024, 2)
            })

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"🧹 Deleted temporary file: {temp_path}")

    except requests.exceptions.RequestException as req_err:
        logger.exception("🔌 Error communicating with Picsart API.")
        return jsonify({'error': f'Error connecting to Picsart API: {str(req_err)}'}), 502

    except Exception as e:
        logger.exception("💥 General failure in image processing.")
        return jsonify({'error': f'Failed to process featured image: {str(e)}'}), 500
    
def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "", name)
