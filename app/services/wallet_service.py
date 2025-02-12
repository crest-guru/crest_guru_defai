from web3 import Web3
from typing import Dict
from app.core.wallet.safe_factory import SafeWalletFactory
from app.core.wallet.cobo_factory import CoboArgusFactory
from config.settings import Settings
from app.db.database import get_wallet, create_wallet_record, update_cobo_address

class WalletService:
    """Service for managing wallet operations"""
    
    def __init__(self, web3: Web3, settings: Settings):
        self.web3 = web3
        self.settings = settings
        self.safe_factory = SafeWalletFactory(web3, settings)
        self.cobo_factory = CoboArgusFactory(web3, settings)
    
    def create_safe_wallet(self, user_address: str) -> Dict[str, str]:
        """Create Safe wallet with Cobo Argus"""
        try:
            # Check if user already has a wallet
            try:
                existing_wallet = get_wallet(user_address)
                if existing_wallet:
                    raise ValueError(f"User {user_address} already has a Safe wallet")
            except ValueError:
                pass
            
            # 1. Create Safe wallet
            safe_address = self.safe_factory.create_safe_from_deployer()
            
            # 2. Create Cobo Argus for Safe
            cobo_address = self.cobo_factory.create_cobo_for_safe(
                safe_address=safe_address,
                user_address=user_address
            )
            
            # Setup Cobo authorizers
            self.cobo_factory.setup_cobo_authorizers(cobo_address)
            
            # 3. Save both addresses to database
            create_wallet_record(user_address, safe_address)
            update_cobo_address(user_address, cobo_address)
            
            return {
                'safe_address': safe_address,
                'cobo_address': cobo_address,
                'status': 'completed'
            }
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}") 