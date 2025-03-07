from web3 import Web3
from eth_account import Account
from pathlib import Path
import os
import json
from config.settings import Settings
from app.core.wallet.authorizer_manager import AuthorizerManager

class CoboArgusFactory:
    """Factory for creating Cobo Argus wallets"""
    
    def __init__(self, web3: Web3, settings: Settings):
        self.web3 = web3
        self.settings = settings
        self.argus_helper_address = settings.ARGUS_HELPER_ADDRESS
        self.helper_contract = self._init_helper_contract()
    
    def create_cobo_for_safe(self, safe_address: str, user_address: str) -> str:
        """Create Cobo Argus for Safe wallet
        
        Args:
            safe_address: Address of Safe wallet
            user_address: User's address to generate salt
            
        Returns:
            str: Address of created Cobo Argus
        """
        
        safe_contract = self._get_safe_contract(safe_address)
        
       
        salt = self.web3.to_bytes(hexstr=f"{user_address}{'32'}").rjust(32, b'\0')
        
        init_data = self.helper_contract.encode_abi(
            "initArgus",
            args=[self.settings.COBO_FACTORY_ADDRESS, salt]
        )
        
        
        tx_hash = safe_contract.functions.getTransactionHash(
            self.argus_helper_address,  # to
            0,                          # value
            init_data,                  # data
            1,                          # operation
            0,                          # safeTxGas
            0,                          # baseGas
            0,                          # gasPrice
            "0x0000000000000000000000000000000000000000",  # gasToken
            "0x0000000000000000000000000000000000000000",  # refundReceiver
            safe_contract.functions.nonce().call()          # nonce
        ).call()
        
        
        signed = Account._sign_hash(tx_hash, self.settings.DEPLOYER_PRIVATE_KEY)
        
        tx = safe_contract.functions.execTransaction(
            self.argus_helper_address,  # to
            0,                          # value
            init_data,                  # data
            1,                          # operation
            0,                          # safeTxGas
            0,                          # baseGas
            0,                          # gasPrice
            "0x0000000000000000000000000000000000000000",  # gasToken
            "0x0000000000000000000000000000000000000000",  # refundReceiver
            signed.signature                                # signature
        ).build_transaction({
            'from': self.settings.DEPLOYER_ADDRESS,
            'gas': 2000000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        })
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        
        
        try:
            return self._get_cobo_address_from_receipt(receipt)
        except Exception as e:
            print("Failed to get Cobo address from receipt:", str(e))
            print("Full receipt:", receipt)
            return None
    
    def _init_helper_contract(self):
        """Initialize Argus helper contract"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", "ArgusAccountHelper.json")
        with open(abi_path, "r") as f:
            helper_abi = json.load(f)
            
        return self.web3.eth.contract(
            address=self.argus_helper_address,
            abi=helper_abi
        )
    
    def _get_safe_contract(self, address: str):
        """Get Safe contract instance"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", "SafeWallet.json")
        with open(abi_path, "r") as f:
            contract_abi = json.load(f)
            
        return self.web3.eth.contract(
            address=address,
            abi=contract_abi
        )
    
    def _get_cobo_address_from_receipt(self, receipt) -> str:
        """Get Cobo address from transaction receipt"""
        
        ARGUS_INITIALIZED_TOPIC = "d98315a38819f85a0914498fdc92737e16297453017a69ca222331e83644e739"
        
        for log in receipt['logs']:
            topic0 = log['topics'][0].hex()

            if topic0.lower() == ARGUS_INITIALIZED_TOPIC.lower():
                raw_address = "0x" + log['topics'][1].hex()[-40:]
                cobo_address = self.web3.to_checksum_address(raw_address)
                return cobo_address
        
        raise Exception("ArgusInitialized event not found in receipt")
    
    def setup_cobo_authorizers(self, cobo_address: str) -> str:
        """Setup Cobo Argus authorizers
        
        Args:
            cobo_address: Address of Cobo Argus
            
        Returns:
            str: Address of created authorizer
        """
        authorizer_manager = AuthorizerManager(self.web3, self.settings)
        authorizer_type = "ApproveAuthorizerV2"
        
        
        authorizer_address = authorizer_manager.create_authorizer(
            cobo_address, 
            authorizer_type
        )
        
        return authorizer_address
    
    def _get_safe_address_from_cobo(self, cobo_address: str) -> str:
        """Get Safe address from Cobo contract"""
        cobo_contract = self.web3.eth.contract(
            address=cobo_address,
            abi=self._get_safe_contract_abi("CoboSafeAccount")
        )
        return cobo_contract.functions.safe().call()
    
    def _get_safe_contract_abi(self, name: str) -> dict:
        """Get contract ABI from Safe contract"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", f"{name}.json")
        with open(abi_path, "r") as f:
            return json.load(f) 