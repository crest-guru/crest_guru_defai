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
            "origins": [
                "http://localhost:5000",
                "http://127.0.0.1:5000",
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "x-api-key"]
        }
    })
    
    
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(info_bp, url_prefix='/api')
    app.register_blueprint(ai_request_bp, url_prefix='/api')
    
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