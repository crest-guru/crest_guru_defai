from web3 import Web3
from config.settings import Settings
from app.core.protocols.token import TokenProtocol

settings = Settings()

def get_wallet_balance(wallet_address: str) -> float:
    web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    balance = web3.eth.get_balance(wallet_address)
    return balance / 10**18

def make_approve_transaction(wallet_address: str, token_address: str, spender_address: str, amount: float) -> str:
    web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    token_protocol = TokenProtocol(web3, settings, wallet_address)
    
    tx_hash = token_protocol.approve(
        token_address=token_address,
        spender_address=spender_address,
        amount=amount
    )
    return (f'Transaction successful, tx_hash: {tx_hash}')

def get_token_balance_for_wallet(wallet_address: str, token_address: str) -> str:
    web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    token_protocol = TokenProtocol(web3, settings, wallet_address)
    return (f'Token balance: {token_protocol.get_token_balance(token_address)}')

