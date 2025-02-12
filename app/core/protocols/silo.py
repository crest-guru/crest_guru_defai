from web3 import Web3
from eth_abi import encode
from typing import Dict, Any, Optional, List
from .base import BaseProtocol
from config.initial_address_setup import INITIAL_SILOS
from config.settings import Settings
import os
import json
from pathlib import Path


class SiloProtocol(BaseProtocol):
    """Protocol for Silo operations"""
    
    def __init__(self, web3: Web3, settings, user_address: str):
        super().__init__(web3, settings, user_address)


    def deposit(
        self,
        silo_address: str,
        amount: int,
    ) -> str:
        """Deposit tokens into Silo
        
        Args:
            silo_address: Silo contract address
            amount: Amount of tokens
            
        Returns:
            str: Transaction hash
        """
        
        
        call_data = self.build_transaction(
            action="deposit",
            silo_address=silo_address,
            amount=amount,
        )
        return self._execute_transaction(call_data)
    
    def deposit_native(
        self,
        silo_address: str,
        amount: int
    ) -> str:
        """Deposit native tokens into Silo
        
        Args:
            silo_address: Silo contract address
            amount: Amount of tokens
            
        Returns:
            str: Transaction hash
        """

        options = encode(
            ['uint256', 'uint8'],
            [amount, 0]
        )

        
        action = {
            'actionType': 0,  # Deposit
            'silo': silo_address,
            'asset': "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38",  # wS
            'options': options
        }

        router_address = "0x22AacdEc57b13911dE9f188CF69633cC537BdB76"
        router_contract = self.web3.eth.contract(
            address=router_address,
            abi=self._load_abi("SiloRouter")
        )

        data = router_contract.encode_abi(
            "execute",
            args=[[action]]
        )
        
        
        
        call_data = {
                'flag': 0,            # Standard call
                'to': router_address,  # Target contract
                'value': amount,           #  value
                'data': bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),  # Encoded function call
                'hint': b'',          # No hint
                'extra': b''          # No extra data
            }
        return self._execute_transaction(call_data)
    
    def withdraw(
        self,
        silo_address: str,
        amount: int,
    ) -> str:
        """Withdraw tokens from Silo
        
        Args:
            silo_address: Silo contract address
            token_address: Token to withdraw
            amount: Amount of tokens
            silo_id: ID of the silo
            recipient: Address to receive tokens (defaults to user)
            
        Returns:
            str: Transaction hash
        """
        
            
        call_data = self.build_transaction(
            action="withdraw",
            silo_address=silo_address,
            amount=amount
        )
        return self._execute_transaction(call_data)

    def build_transaction(
        self,
        action: str,
        silo_address: str,
        amount: int,
    ) -> Dict[str, Any]:
        """Build transaction data for token operations
        
        Args:
            action: Operation type ('deposit', 'withdraw', etc)
            silo_address: Silo contract address
            amount: Amount of tokens
        Returns:
            Dict[str, Any]: CallData struct for Cobo execTransaction
        """
        
        if action == "deposit":
            silo_market_contract = self.web3.eth.contract(
                address=silo_address,
                abi=self._load_abi("SiloMarket")
            )
            data = silo_market_contract.encode_abi(
                "deposit",
                args=[amount]
            )      
            
            return {
                'flag': 0,            # Standard call
                'to': silo_address,  # Target contract
                'value': 0,           #  value
                'data': bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),  # Encoded function call
                'hint': b'',          # No hint
                'extra': b''          # No extra data
            }
        
        if action == "withdraw":
            silo_market_contract = self.web3.eth.contract(
                address=silo_address,
                abi=self._load_abi("SiloMarket")
            )

            data = silo_market_contract.encode_abi(
                "redeem",
                args=[amount, self.safe_address, self.safe_address, 0]
            )

            return {
                'flag': 0,            # Standard call
                'to': silo_address,  # Target contract
                'value': 0,           # ETH value
                'data': bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),  # Encoded function call
                'hint': b'',          # No hint
                'extra': b''          # No extra data
            }

        raise ValueError(f"Unknown action: {action}")
    
    @classmethod
    def _load_lens_abi(cls) -> dict:
        """Load SiloLens contract ABI"""
        abi_path = os.path.join(
            Path(__file__).parent.parent.parent,
            "abi",
            "SiloLens.json"
        )
        
        with open(abi_path, 'r') as f:
            return json.load(f)

    @classmethod
    def get_apr(cls, web3: Web3, settings: Settings) -> List[Dict[str, Any]]:
        """Get APR for all registered silos (static method)
        
        Args:
            web3: Web3 instance
            settings: Application settings
            
        Returns:
            List[Dict[str, Any]]: List of APRs for each silo
        """
        silo_lens = web3.eth.contract(
            address="0xE05966aee69CeCD677a30f469812Ced650cE3b5E",
            abi=cls._load_lens_abi()
        )
        
        results = []
        for silo in INITIAL_SILOS:
            apr = silo_lens.functions.getDepositAPR(silo).call()
            results.append({
                "silo_address": silo,
                "apr": apr / 10**18 * 100
            })
        
        return results