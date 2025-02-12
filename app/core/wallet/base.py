from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseWallet(ABC):
    
    
    def __init__(self, address: str):
        self.address = address
    
    @abstractmethod
    async def get_balance(self) -> float:
        
        pass
    
    @abstractmethod
    async def send_transaction(self, tx_data: Dict[str, Any]):
        
        pass 