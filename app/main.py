import sys
import os
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from flask import Flask
from flask_cors import CORS
from api.wallet import wallet_bp
from api.info import info_bp
from api.ai_request import ai_request_bp

settings = Settings()

def create_app():
    """Initialize all application components"""
    
    settings = Settings()
    app = Flask(__name__)
    

    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"], 
            "allow_headers": [
                "Content-Type", 
                "x-api-key", 
                "Authorization",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Origin",
                "Accept",
                "X-Requested-With"
            ],
            "expose_headers": [
                "Content-Type", 
                "Authorization",
                "Access-Control-Allow-Origin"
            ],
            "supports_credentials": True,
            "max_age": 86400  
        }
    })
    
    
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(info_bp, url_prefix='/api')
    app.register_blueprint(ai_request_bp, url_prefix='/api')
    
    @app.after_request
    def after_request(response):
        """Add headers to every response"""
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-api-key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response
    
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