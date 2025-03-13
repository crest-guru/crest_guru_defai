from flask import Blueprint, jsonify, request
from web3 import Web3
from app.core.protocols.silo import SiloProtocol
from config.settings import Settings
from typing import Dict, Any

settings = Settings()
web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))

info_bp = Blueprint('info', __name__)

@info_bp.route('/', methods=['GET', 'POST'])
def info() -> Dict[str, Any]:
    """Get protocol information
    
    Query params:
        protocol: str - Protocol name (e.g. 'silo')
        method: str - Method name (e.g. 'all_apr')
    
    Returns:
        JSON response with protocol information
    """
    try:
        protocol = request.args.get('protocol')
        method = request.args.get('method')
        
        if not protocol or not method:
            return jsonify({
                'error': 'Required query params: protocol, method'
            }), 400
            
        if protocol == 'silo':
            if method == 'all_apr':
                # use static method
                apr_data = SiloProtocol.get_apr(web3, settings)
                return jsonify({
                    'status': 'success',
                    'data': {
                        'apr': apr_data
                    }
                })
            else:
                return jsonify({
                    'error': f'Unknown method for silo protocol: {method}'
                }), 400
        else:
            return jsonify({
                'error': f'Unknown protocol: {protocol}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500