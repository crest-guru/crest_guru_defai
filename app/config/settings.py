import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

class Settings:
    
    
    def __init__(self):
        # get absolute path to project root directory
        root_dir = Path(__file__).parent.parent.parent
        env_path = root_dir / '.env'
        
        # load .env file
        load_dotenv(env_path, override=True)
        
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', '5010'))
        self.FRONTEND_URL = os.getenv('FRONTEND_URL', 'localhost:5011')
        
        self.RPC_URL = os.getenv('RPC_URL', 'https://rpc.soniclabs.com')
        self.CHAIN_ID = int(os.getenv('CHAIN_ID', '146'))
        self.SAFE_SERVICE_URL = os.getenv('SAFE_SERVICE_URL', 'https://safe-transaction.sonic.guru')
        self.AI_SERVICE_URL = os.getenv('AI_SERVICE_URL')
        self.AI_SERVICE_KEY = os.getenv('AI_SERVICE_KEY')
        self.SAFE_FACTORY_ADDRESS = os.getenv('SAFE_FACTORY_ADDRESS', "0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67")
        self.COBO_FACTORY_ADDRESS = os.getenv('COBO_FACTORY_ADDRESS', "0x14149ab9476c12ab55ef6831cbE973B77De7f2Ac")
        self.ARGUS_HELPER_ADDRESS = os.getenv('ARGUS_HELPER_ADDRESS', "0xBBb7412f5dAc3Ed358C42E34b51BA2256fb3EB17")
        self.MULTISEND_ADDRESS = os.getenv('MULTISEND_ADDRESS', "0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526")    


        # Deployer settings
        self.DEPLOYER_ADDRESS = os.getenv('DEPLOYER_ADDRESS')
        self.DEPLOYER_PRIVATE_KEY = os.getenv('DEPLOYER_PRIVATE_KEY')
        
        # Validation
        if not self.DEPLOYER_ADDRESS or not self.DEPLOYER_PRIVATE_KEY:
            raise ValueError("Deployer address and private key are required")
        
        # Safe contract addresses
        self.SAFE_SINGLETON_ADDRESS = os.getenv('SAFE_SINGLETON_ADDRESS', "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762")
        self.FALLBACK_HANDLER_ADDRESS = os.getenv(
            'FALLBACK_HANDLER_ADDRESS',
            '0x0000000000000000000000000000000000000000'
        )

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    ENABLE_TELEGRAM_BOT: bool = False
    TELEGRAM_TOKEN: Optional[str] = None
    
    OPENAI_API_KEY: Optional[str] = None
    
    # Authorizer implementations
    APPROVE_AUTHORIZER_IMPL = os.getenv('APPROVE_AUTHORIZER_IMPL', "0x65949fD26c04DbA182F1B8C277A4BfA4fC77dACa")
    SILO_AUTHORIZER_IMPL = os.getenv('SILO_AUTHORIZER_IMPL', "0x425ab37703a7eE412e8187505055c82870D60B65")
    # can add other authorizer types here
