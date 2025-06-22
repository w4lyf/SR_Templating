from flask import Flask, render_template

# Import Blueprints
from routes.game_info import game_info_bp
from routes.thumbnail import thumbnail_bp
from routes.featured_image import featured_bp
from routes.seo import seo_bp
from routes.game_page import game_page_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(game_info_bp)
app.register_blueprint(thumbnail_bp)
app.register_blueprint(featured_bp)
app.register_blueprint(seo_bp)
app.register_blueprint(game_page_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
