from web3 import Web3
from typing import Dict, Any, Optional
from .base import BaseProtocol

class TokenProtocol(BaseProtocol):
    """Protocol for token operations (ERC20)"""
    
    MAX_UINT256 = 2**256 - 1
    
    def __init__(self, web3: Web3, settings, user_address: str):
        super().__init__(web3, settings, user_address)
        
    def approve(
        self,
        token_address: str,
        spender_address: str,
        amount: str = None  
    ) -> str:
        """Approve tokens for spender
        
        Args:
            token_address: Token contract address
            spender_address: Spender address
            amount: Amount of tokens (in wei as string)
        """
        try:
            print(f"[TokenProtocol] Starting approve with params:")
            print(f"  token_address: {token_address}")
            print(f"  spender_address: {spender_address}")
            print(f"  amount: {amount}")
            
            if amount is None:
                amount = "115792089237316195423570985008687907853269984665640564039457584007913129639935"
            
            token_contract = self.web3.eth.contract(
                address=token_address,
                abi=self._load_abi("ERC20")
            )
            
            
            data = token_contract.encode_abi(
                "approve",
                args=[
                    spender_address,
                    int(amount)
                ]
            )
            
            
            call_data = {
                'flag': 0,
                'to': token_address,
                'value': 0,
                'data': bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),
                'hint': b'',
                'extra': b''
            }
           
            
            try:
                result = self._execute_transaction(call_data)
                
                return result
            except Exception as e:
                
                raise
            
        except Exception as e:
            print(f"[TokenProtocol] Error in approve: {str(e)}")
            raise
        
    def get_allowance(
        self, 
        token_address: str, 
        spender_address: str
    ) -> int:
        """Get current allowance
        
        Args:
            token_address: Token contract address
            spender_address: Spender address
            
        Returns:
            int: Current allowance
        """
        token_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(token_address),
            abi=self._load_abi("ERC20")
        )
        
        return token_contract.functions.allowance(
            self.safe_address,  # owner
            spender_address     # spender
        ).call()

    def get_token_balance(
        self,
        token_address: str
    ) -> int:
        token_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(token_address),
            abi=self._load_abi("ERC20")
        )
        
        return token_contract.functions.balanceOf(
            self.safe_address
        ).call()

    def build_transaction(
        self,
        action: str,
        token_address: str,
        spender_address: str = None,
        amount: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build transaction data for token operations
        
        Args:
            action: Operation type ('approve', 'transfer', etc)
            token_address: Token contract address
            spender_address: Spender address (for approve)
            amount: Amount of tokens
            
        Returns:
            Dict[str, Any]: CallData struct for Cobo execTransaction
        """
        token_contract = self.web3.eth.contract(
            address=token_address,
            abi=self._load_abi("ERC20")
        )
        
        if action == "approve":
            if not spender_address:
                raise ValueError("spender_address required for approve")
            
            amount = amount if amount is not None else self.MAX_UINT256
            data = token_contract.encode_abi(
                "approve",
                args=[spender_address, amount]
            )
            
            
            return {
                'flag': 0,            # Standard call
                'to': token_address,  # Target contract
                'value': 0,           # ETH value
                'data': bytes.fromhex(data[2:]) if data.startswith('0x') else bytes.fromhex(data),  # Encoded function call
                'hint': b'',          # No hint
                'extra': b''          # No extra data
            }
        
        raise ValueError(f"Unknown action: {action}")