from flask import Blueprint, request, jsonify
from services.html_generator import generate_html_content

game_page_bp = Blueprint('game_page', __name__)

@game_page_bp.route('/generate_page', methods=['POST'])
def generate_page():
    try:
        data = request.get_json()
        print(data)
        # Validate required fields
        required_fields = ['game_name']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400

        
        html_content = generate_html_content(
            game_name=data['game_name'],
            about_html=data['about_html'],
            sysreq_html=data.get('minimum_sysreq_html', ''),
            genres=data.get('genres', []),
            developer=data.get('developer', ''),
            game_size=data.get('game_size', ''),
            released_by=data.get('released_by', ''),
            version=data.get('version', ''),
            screenshot1_url=data.get('ss1_url', ''),
            screenshot2_url=data.get('ss2_url', ''),
            gofile_link=data.get('gofile_link', ''),
            buzzheavier_link=data.get('buzzheavier_link', '')
        )

        return jsonify({
            'success': True,
            'message': 'HTML code generated successfully!',
            'html_content': html_content
        })

    except Exception as e:
        return jsonify({'error': f'Failed to generate code: {str(e)}'}), 500
