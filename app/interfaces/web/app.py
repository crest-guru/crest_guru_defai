from flask import Flask
from flask_cors import CORS
from config.settings import Settings

def create_app(settings: Settings) -> Flask:
    """Create Flask application"""
    app = Flask(__name__)
    CORS(app)
    
    
    app.config.from_object(settings)
    
   
    from api.auth import auth_bp
    from api.wallet import wallet_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    
    return app 