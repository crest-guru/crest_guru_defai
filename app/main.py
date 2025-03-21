import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from flask import Flask
from flask_cors import CORS
from api.wallet import wallet_bp
from api.info import info_bp
from api.ai_request import ai_request_bp

settings = Settings()

def create_app():
    settings = Settings()
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    frontend_url = settings.FRONTEND_URL
    
    ALLOWED_ORIGINS = [
        "http://localhost:5011",
        frontend_url,

    ]
    
    @app.before_request
    def check_origin():
        from flask import request, abort
        origin = request.headers.get('Origin')
        print(f"Received request from origin: {origin}")  # Debug line

        if origin and origin not in ALLOWED_ORIGINS:
            print(f"Blocking request from: {origin}")
            abort(403)
        print(f"Allowing request from: {origin}")


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response

    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 200
    CORS(app, resources={r"/api/*": {
        "origins": "*", 
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"], 
        "allow_headers": ["Content-Type", "Authorization", "Origin", "X-Requested-With"]}})
    # CORS(app, resources={
    #     r"/api/*": {
    #         "origins": ALLOWED_ORIGINS,
    #         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    #         "allow_headers": [
    #             "Content-Type",
    #             "x-api-key",
    #             "Authorization",
    #             "Origin",
    #             "Accept",
    #             "X-Requested-With",
    #             "Access-Control-Request-Method",
    #             "Access-Control-Request-Headers"
    #         ],
    #         "expose_headers": [
    #             "Access-Control-Allow-Origin",
    #             "Access-Control-Allow-Credentials"
    #         ],
    #         "supports_credentials": True,
    #         "max_age": 86400
    #     }
    # })
    
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(info_bp, url_prefix='/api/info')
    app.register_blueprint(ai_request_bp, url_prefix='/api/ai_request')
    
    return app
def main():
    """Application entry point"""
    try:
        app = create_app()
        
        
        if __name__ == "__main__":
            app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
            
    except Exception as e:
        print(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main() 