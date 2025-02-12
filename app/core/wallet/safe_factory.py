from web3 import Web3
from typing import Dict, Any
import json
import os
from config.settings import Settings
from pathlib import Path
from app.core.wallet.safe_wallet import SafeWallet

class SafeWalletFactory:
    """Factory for creating Safe wallets"""
    
    def __init__(self, web3: Web3, settings: Settings):
        self.web3 = web3
        self.settings = settings
        self.factory_address = settings.SAFE_FACTORY_ADDRESS
        self.factory_contract = self._init_factory_contract()
    
    def _init_factory_contract(self):
        """Initialize Safe factory contract"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", "SafeProxyFactory.json")
        with open(abi_path, "r") as f:
            factory_abi = json.load(f)
        
        return self.web3.eth.contract(
            address=self.factory_address,
            abi=factory_abi
        )
    
    def create_safe_from_deployer(self) -> str:
        """Create new Safe wallet from deployer account"""
        setup_data = self._prepare_safe_setup(self.settings.DEPLOYER_ADDRESS)
        salt_nonce = self.web3.eth.block_number
        
        tx = self.factory_contract.functions.createProxyWithNonce(
            self.settings.SAFE_SINGLETON_ADDRESS,
            setup_data,
            salt_nonce
        ).build_transaction({
            'from': self.settings.DEPLOYER_ADDRESS,
            'gas': 2000000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price
        })
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return self._get_safe_address_from_receipt(receipt)

    def transfer_ownership(self, safe_address: str, new_owner: str) -> str:
        """Transfer Safe ownership to new owner
        
        Args:
            safe_address: Address of Safe wallet
            new_owner: New owner address
            
        Returns:
            str: Transaction hash
        """
        safe = SafeWallet(self.web3, self.settings, safe_address)
        
        old_owner = self.settings.DEPLOYER_ADDRESS
        
       
        data = safe.contract.encode_abi(
            "swapOwner",
            args=[
                "0x0000000000000000000000000000000000000001",  # prevOwner (sentinel)
                old_owner,                                      # oldOwner (deployer)
                new_owner                                       # newOwner
            ]
        )
        
        tx_hash = safe.execute_transaction(
            to=safe_address,     
            data=bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),
            operation=0          # Call
        )
        
        return tx_hash

    def _prepare_safe_setup(self, owner_address: str) -> bytes:
        """Prepare data for Safe setup
        
        Args:
            owner_address: Address that will be the owner of Safe
            
        Returns:
            bytes: Encoded setup data for Safe creation
        """
        
        singleton_address = self._get_singleton_address()
        safe_contract = self._get_safe_contract(singleton_address)
        
        
        owners = [owner_address]  # List of initial owners
        threshold = 1  # Number of required confirmations
        to = "0x0000000000000000000000000000000000000000"  # Optional delegate call after setup
        data = b""  # Data for delegate call
        fallback_handler = self.settings.FALLBACK_HANDLER_ADDRESS  # Default handler for fallback calls
        payment_token = "0x0000000000000000000000000000000000000000"  # Token for payment
        payment = 0  # Payment value
        payment_receiver = "0x0000000000000000000000000000000000000000"  # Payment receiver
        
        
        setup_data = safe_contract.encode_abi(
            "setup",
            args=[
                owners,              # _owners
                threshold,          # _threshold
                to,                # to
                data,              # data
                fallback_handler,  # fallbackHandler
                payment_token,     # paymentToken
                payment,          # payment
                payment_receiver  # paymentReceiver
            ]
        )
        
        return setup_data

    def _get_singleton_address(self) -> str:
        """Get address of Safe singleton contract
        
        Returns:
            str: Address of Safe singleton
        """
        return self.settings.SAFE_SINGLETON_ADDRESS

    def _get_safe_contract(self, address: str):
        """Get Safe contract instance"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", "SafeWallet.json")
        with open(abi_path, "r") as f:
            contract_abi = json.load(f)
        
        return self.web3.eth.contract(
            address=address,
            abi=contract_abi
        )

    def _get_safe_address_from_receipt(self, receipt) -> str:
        """Extract Safe address from transaction receipt
        
        Args:
            receipt: Transaction receipt from createProxyWithNonce
            
        Returns:
            str: Address of created Safe
        """
        
        proxy_creation_event = self.factory_contract.events.ProxyCreation().process_receipt(receipt)
        
        if not proxy_creation_event:
            raise Exception("ProxyCreation event not found in receipt")
        
        
        proxy_address = proxy_creation_event[0]['args']['proxy']
        return proxy_address