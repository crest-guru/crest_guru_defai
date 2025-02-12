from web3 import Web3
from typing import Dict, Any
from abc import ABC, abstractmethod
from app.db.database import get_wallet
import json
import os
from pathlib import Path

class BaseProtocol(ABC):
    """Base protocol for DeFi interactions"""
    
    def __init__(self, web3: Web3, settings, user_address: str):
        self.web3 = web3
        self.settings = settings
        self.user_address = user_address
        
        
        wallet_data = get_wallet(user_address)
        self.safe_address = wallet_data['safe_address']
        self.cobo_address = wallet_data['cobo_address']
        
        self.agent_address = wallet_data['agent_address']
        self.agent_key = wallet_data['agent_key']
    
    def _execute_transaction(self, call_data: Dict[str, Any]) -> str:
        """Execute transaction through Cobo"""
        cobo_contract = self.web3.eth.contract(
            address=self.cobo_address,
            abi=self._load_abi("CoboSafeAccount")
        )
        
        
        tx = cobo_contract.functions.execTransaction(call_data).build_transaction({
            'from': self.agent_address,
            'gas': 800000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.agent_address),
            'chainId': self.settings.CHAIN_ID
        })
        
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, 
            private_key=self.agent_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash.hex()
    
    def _execute_transaction_with_native(self, call_data: Dict[str, Any], native_amount: int) -> str:
        """Execute transaction through Cobo with native token"""
        cobo_contract = self.web3.eth.contract(
            address=self.cobo_address,
            abi=self._load_abi("CoboSafeAccount")
        )
        tx = cobo_contract.functions.execTransaction(call_data).build_transaction({
            'from': self.agent_address,
            'value': native_amount,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.agent_address),
            'chainId': self.settings.CHAIN_ID
        })
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, 
            private_key=self.agent_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash.hex()
    
    @classmethod
    def _load_abi(cls, name: str) -> dict:
        """Load contract ABI from json file
        
        Args:
            name: Name of the contract (without .json)
            
        Returns:
            dict: Contract ABI
            
        Raises:
            FileNotFoundError: If ABI file not found
        """
        abi_path = os.path.join(
            Path(__file__).parent.parent.parent,
            "abi",
            f"{name}.json"
        )
        
        try:
            with open(abi_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"ABI file not found: {abi_path}")
    
    @abstractmethod
    def build_transaction(self, **kwargs) -> Dict[str, Any]:
        """Build transaction data for protocol
        
        Should be implemented by specific protocols
        """
        pass 