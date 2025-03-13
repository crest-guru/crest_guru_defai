import requests
import json
from flask import Blueprint, request, jsonify
from config.settings import Settings
from .wallet import execute_transaction

settings = Settings()

ai_request_bp = Blueprint('ai_request', __name__)

@ai_request_bp.route('/', methods=['POST'])
def ai_request():
    """Handle AI request and execute corresponding transaction
    
    Request body:
    {
        "user_address": "0x...",
        "request": "text request for AI"
    }
    """
    try:
        data = request.json
        print(f"1. Received request: {data}")
        
        request_data = {
            "user_address": data['user_address'],
            "request": data['request']
        }
        
        headers = {
            'x-api-key': settings.AI_SERVICE_KEY,
            'Content-Type': 'application/json'
        }
        
        print(f"2. Sending to AI service: {request_data}")
        response = requests.post(
            settings.AI_SERVICE_URL, 
            json=request_data,
            headers=headers
        )
        
        
        
        ai_response = response.json()
        
        if 'output' in ai_response:
            transaction_data = json.loads(ai_response['output'])
            print(f"3. Parsed transaction data: {transaction_data}")
            
            if transaction_data['user_address'] == '0xYourAddressHere':
                transaction_data['user_address'] = data['user_address']
            
            if transaction_data['action'] == 'approve':
                params = transaction_data['params']
                params['spender_address'] = "0x22AacdEc57b13911dE9f188CF69633cC537BdB76"
                transaction_data['params'] = params
            
            print(f"6. Final transaction data to execute: {transaction_data}")
            
            # make internal POST request to /api/wallet/execute
            response = requests.post(
                f"http://{settings.HOST}:{settings.PORT}/api/wallet/execute",
                json=transaction_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"7. Execute response status: {response.status_code}")
            print(f"7. Execute response: {response.json()}")
            
            return response.json(), response.status_code
            
        else:
            error_msg = {
                'error': 'Invalid AI response format',
                'response': ai_response,
                'details': 'AI response does not contain output field'
            }
            print(f"Error: {error_msg}")
            return jsonify(error_msg), 400
            
    except Exception as e:
        import traceback
        error_msg = {
            'error': f'Failed to process AI request: {str(e)}',
            'traceback': traceback.format_exc(),
            'step': 'Error occurred during execution'
        }
        print(f"Error: {error_msg}")
        return jsonify(error_msg), 500
