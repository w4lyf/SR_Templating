from flask import Blueprint, request, jsonify
from services.steam_scraper import fetch_game_info
import requests

game_info_bp = Blueprint('game_info', __name__)

@game_info_bp.route('/fetch_game_info', methods=['POST'])
def fetch_game_info_route():
    try:
        data = request.get_json()
        appid = data.get('appid', '').strip()
        
        if not appid:
            return jsonify({'error': 'App ID is required'}), 400
            
        info = fetch_game_info(appid)
        return jsonify(info)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch game data: {str(e)}'}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
