from web3 import Web3   
from config.settings import Settings
from app.core.protocols.crowdfinding import CrowdfindingProtocol
settings = Settings()

def make_contribution(wallet_address: str, amount: int) -> str:
    web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    crowdfinding_protocol = CrowdfindingProtocol(web3, settings, wallet_address)
    tx_hash = crowdfinding_protocol.make_contribution(
        amount=amount
    )
    return (f'Transaction successful, tx_hash: {tx_hash}')
