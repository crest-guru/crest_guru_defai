from flask import Blueprint, request, jsonify
from services.wallet_service import WalletService
from config.settings import Settings
from web3 import Web3
from app.db.database import create_wallet_record, update_cobo_address, get_wallet
from app.core.wallet.safe_factory import SafeWalletFactory
from app.core.wallet.cobo_factory import CoboArgusFactory
from app.core.wallet.authorizer_manager import AuthorizerManager
from app.core.protocols.token import TokenProtocol
from app.core.protocols.silo import SiloProtocol
from app.core.protocols.registry import ProtocolRegistry

wallet_bp = Blueprint('wallet', __name__)
settings = Settings()
web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
wallet_service = WalletService(web3, settings)

@wallet_bp.route('/', methods=['POST'])
@wallet_bp.route('', methods=['POST'])
def create_wallet():
    """Create new wallet for user"""
    try:
        user_address = request.json.get('address')
        if not user_address:
            return jsonify({'error': 'Address required'}), 400
            
        # 1. create safe
        safe_factory = SafeWalletFactory(web3, settings)
        safe_address = safe_factory.create_safe_from_deployer()
        
        # 2. write wallet to db
        create_wallet_record(user_address, safe_address)
        
        # 3. create cobo
        cobo_factory = CoboArgusFactory(web3, settings)
        cobo_address = cobo_factory.create_cobo_for_safe(
            safe_address=safe_address,
            user_address=user_address
        )
        
        # 4. update cobo address in db
        update_cobo_address(user_address, cobo_address)
        
        # 5. setup authorizers
        authorizer_manager = AuthorizerManager(web3, settings)

        # create approve authorizer
        approve_authorizer_address = authorizer_manager.create_authorizer(
            cobo_address=cobo_address,
            user_address=user_address,
            authorizer_type="ApproveAuthorizerV2",
            role_name="approve"
        )

        # create silo authorizer
        silo_authorizer_address = authorizer_manager.create_authorizer(
            cobo_address=cobo_address,
            user_address=user_address,
            authorizer_type="SiloAuthorizer",
            role_name="silo"
        )
        
        # 7. transfer ownership of safe to user
        safe_factory.transfer_ownership(
            safe_address=safe_address,
            new_owner=user_address
        )
        
        return jsonify({
            'safe_address': safe_address,
            'cobo_address': cobo_address,
            'approve_authorizer_address': approve_authorizer_address,
            'silo_authorizer_address': silo_authorizer_address
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

@wallet_bp.route('/execute', methods=['POST'])
def execute_transaction():
    """Execute wallet transaction
    
    Request body:
    {
        "user_address": "0x...",
        "action": "approve" | "silo_deposit" | "silo_withdraw",
        "params": {
            # for approve:
            "token_address": "0x...",
            "spender_address": "0x...",
            "amount": "1000000000000000000"
            
            # for silo_deposit:
            "token_address": "0x...",
            "amount": "1000000000000000000",
            "silo_id": "123"
            
            # for silo_withdraw:
            "token_address": "0x...",
            "amount": "1000000000000000000",
            "silo_id": "123",
            "recipient": "0x..."  # optional, defaults to user_address
        }
    }
    """
    try:
        data = request.json
        print(f"[Execute] Got request data: {data}")
        
        if not all(field in data for field in ['user_address', 'action', 'params']):
            print("[Execute] Missing required fields")
            return jsonify({
                'error': 'Required fields: user_address, action, params'
            }), 400
            
        user_address = data['user_address']
        action = data['action']
        params = data['params']
        
        print(f"[Execute] Getting wallet data for user {user_address}")
        try:
            wallet_data = get_wallet(user_address)
            print(f"[Execute] Got wallet data: {wallet_data}")
        except Exception as db_error:
            print(f"[Execute] Database error: {str(db_error)}")
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
        
        if action == 'approve':
            print(f"[Execute] Processing approve action with params: {params}")
            try:
                token_protocol = TokenProtocol(web3, settings, user_address)
                tx_hash = token_protocol.approve(
                    token_address=params['token_address'],
                    spender_address=params['spender_address'],
                    amount=params.get('amount')
                )
                print(f"[Execute] Approve successful, tx_hash: {tx_hash}")
                return jsonify({
                    'tx_hash': tx_hash,
                    'status': 'success'
                })
            except Exception as tx_error:
                print(f"[Execute] Error in approve: {str(tx_error)}")
                return jsonify({'error': str(tx_error)}), 500
            
        elif action in ['silo_deposit', 'silo_withdraw', 'silo_deposit_native']:
            if not all(field in params for field in ['silo_address', 'amount']):
                return jsonify({
                    'error': 'Required params: silo_address, amount'
                }), 400
                
            protocol_info = ProtocolRegistry.get_protocol_info(action)
            silo_protocol = protocol_info["class"](web3, settings, user_address)
            method = getattr(silo_protocol, protocol_info["method"])
            
            tx_hash = method(
                silo_address=params['silo_address'],
                amount=params['amount']
            )
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
            
        return jsonify({
            'tx_hash': tx_hash,
            'status': 'success'
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallet_bp.route('/methods', methods=['GET'])
def get_available_methods():
    """Get all available API methods with their parameters"""
    try:
        methods = ProtocolRegistry.get_all_methods()
        return jsonify({
            "status": "success",
            "methods": methods
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@wallet_bp.route('/info', methods=['GET'])
def get_wallet_info():
    """Get full wallet info for user
    
    Query params:
        address: User address
        
    Returns:
        {
            "safe_address": "0x...",
            "cobo_address": "0x...",
            "agent_address": "0x...",
            "created_at": "timestamp"
        }
    """
    try:
        user_address = request.args.get('address')
        if not user_address:
            return jsonify({
                'error': 'Address parameter is required'
            }), 400
            
        print(f"[WalletInfo] Getting info for user: {user_address}")
        
        try:
            wallet_data = get_wallet(user_address)
            print(f"[WalletInfo] Found wallet data: {wallet_data}")
            
            return jsonify({
                'status': 'success',
                'data': wallet_data
            })
            
        except ValueError as e:
            print(f"[WalletInfo] No wallet found: {str(e)}")
            return jsonify({
                'error': 'Wallet not found',
                'details': str(e)
            }), 404
            
    except Exception as e:
        print(f"[WalletInfo] Error: {str(e)}")
        return jsonify({
            'error': 'Failed to get wallet info',
            'details': str(e)
        }), 500 