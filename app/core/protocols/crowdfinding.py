from web3 import Web3
from eth_abi import encode
from typing import Dict, Any, Optional, List
from .base import BaseProtocol
from config.initial_address_setup import INITIAL_SILOS
from config.settings import Settings
import os
import json
from pathlib import Path

settings = Settings()

class CrowdfindingProtocol(BaseProtocol):
    """Protocol for Crowdfinding operations"""
    
    def __init__(self, web3: Web3, settings, user_address: str):
        super().__init__(web3, settings, user_address)
        
    def make_contribution(
        self,
        amount: int,
        
    ) -> str:
        """Make a contribution to a crowdfinding contract"""
        call_data = self.build_transaction(
            action="contribute",
            amount=amount
        )
        return self._execute_transaction(call_data)
    
    def build_transaction(
        self,
        action: str,
        amount: int,
    ) -> Dict[str, Any]:
        """Build a transaction for a crowdfinding contract"""
        
        
        crowdfinding_contract = self.web3.eth.contract(
            address="0x9303a680bA1A2924Bb6EeE5A7eD804df2E1824f7", #Crowdfinding contract
            abi=self._load_abi("Crowdfinding")
        )
        data = crowdfinding_contract.encode_abi(
            "contribute",
            args=[amount]
        )
        return {
            "flag": 0,
            "to": "0x9303a680bA1A2924Bb6EeE5A7eD804df2E1824f7", #Crowdfinding contract
            "value": 0,
            "data": bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),
            "hint": b'',
            "extra": b''
        }
    
    