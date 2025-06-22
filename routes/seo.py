from flask import Blueprint, request, jsonify
from services.html_generator import generate_html_content

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/generate_seo', methods=['POST'])
def generate_seo():
    try:
        data = request.get_json()
        game_name = data.get('game_name', '').strip()

        if not game_name:
            return jsonify({'error': 'Game name is required'}), 400

        focus_keyphrase = f"{game_name} SteamRIP com"
        meta_description = f"{game_name} Free Download SteamRIP.com Get {game_name} PC game for free instantly and play pre-installed on SteamRIP"

        return jsonify({
            'focus_keyphrase': focus_keyphrase,
            'meta_description': meta_description
        })

    except Exception as e:
        return jsonify({'error': f'Failed to generate SEO data: {str(e)}'}), 500

