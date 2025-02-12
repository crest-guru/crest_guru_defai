from typing import Dict, Any
from app.core.wallet.base import BaseWallet
from web3 import Web3
import os
import json
from eth_account import Account
from pathlib import Path

class SafeWallet(BaseWallet):
    """Implementation of Safe wallet"""
    
    def __init__(self, web3: Web3, settings, safe_address: str):
        super().__init__(safe_address)
        self.web3 = web3
        self.settings = settings
        self.contract = self._get_contract(safe_address, "SafeWallet")
    
    def execute_transaction(
        self,
        to: str,
        data: bytes,
        operation: int = 0,  # 0=Call, 1=DelegateCall
    ) -> str:
        """Execute transaction through Safe wallet
        
        Args:
            to: Target contract address
            data: Transaction data
            operation: Operation type (0=Call, 1=DelegateCall)
            
        Returns:
            str: Transaction hash
        """
        
        tx_hash = self.contract.functions.getTransactionHash(
            to,                 # to
            0,                 # value
            data,             # data
            operation,        # operation
            0,               # safeTxGas
            0,               # baseGas
            0,               # gasPrice
            "0x0000000000000000000000000000000000000000",  # gasToken
            "0x0000000000000000000000000000000000000000",  # refundReceiver
            self.contract.functions.nonce().call()          # nonce
        ).call()
        
        
        signed = Account._sign_hash(tx_hash, self.settings.DEPLOYER_PRIVATE_KEY)
        
        
        tx = self.contract.functions.execTransaction(
            to,              # to
            0,              # value
            data,          # data
            operation,     # operation
            0,            # safeTxGas
            0,            # baseGas
            0,            # gasPrice
            "0x0000000000000000000000000000000000000000",  # gasToken
            "0x0000000000000000000000000000000000000000",  # refundReceiver
            signed.signature                                # signature
        ).build_transaction({
            'from': self.settings.DEPLOYER_ADDRESS,
            'gas': 600000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        })
        
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt['transactionHash'].hex()

    def _get_contract(self, address: str, name: str):
        """Get contract instance"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", f"{name}.json")
        with open(abi_path, "r") as f:
            contract_abi = json.load(f)
        return self.web3.eth.contract(address=address, abi=contract_abi)
    
    async def get_balance(self) -> float:
        
        balance = await self.web3.eth.get_balance(self.address)
        return self.web3.from_wei(balance, 'ether')
    
    def send_transaction(self, tx_data: Dict[str, Any]) -> str:
        """Send transaction through Safe wallet
        
        Args:
            tx_data: Transaction data containing:
                - to: Target address
                - value: ETH value
                - data: Transaction data
                - operation: Operation type (0=Call, 1=DelegateCall)
                
        Returns:
            str: Transaction hash
        """
        try:
            tx_hash = self.contract.functions.getTransactionHash(
                tx_data['to'],                 # to
                tx_data.get('value', 0),       # value
                tx_data['data'],               # data
                tx_data.get('operation', 0),   # operation
                0,                             # safeTxGas
                0,                             # baseGas
                0,                             # gasPrice
                "0x0000000000000000000000000000000000000000",  # gasToken
                "0x0000000000000000000000000000000000000000",  # refundReceiver
                self.contract.functions.nonce().call()          # nonce
            ).call()
            
            signed = Account._sign_hash(tx_hash, self.settings.DEPLOYER_PRIVATE_KEY)
            
            tx = self.contract.functions.execTransaction(
                tx_data['to'],              # to
                tx_data.get('value', 0),    # value
                tx_data['data'],           # data
                tx_data.get('operation', 0), # operation
                0,                          # safeTxGas
                0,                          # baseGas
                0,                          # gasPrice
                "0x0000000000000000000000000000000000000000",  # gasToken
                "0x0000000000000000000000000000000000000000",  # refundReceiver
                signed.signature                                # signature
            ).build_transaction({
                'from': self.settings.DEPLOYER_ADDRESS,
                'gas': 600000,
                'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
                'gasPrice': self.web3.eth.gas_price,
                'chainId': self.settings.CHAIN_ID
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt['transactionHash'].hex()
            
        except Exception as e:
            print(f"Error sending transaction: {str(e)}")
            raise
    
    