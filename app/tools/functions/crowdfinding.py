from web3 import Web3   
import logging
from config.settings import Settings
from app.core.protocols.crowdfinding import CrowdfindingProtocol
from app.core.protocols.token import TokenProtocol
settings = Settings()


def make_contribution(wallet_address: str, amount: int) -> str:
    amount = amount*10**6
    web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    token_protocol = TokenProtocol(web3, settings, wallet_address)
    allowance = token_protocol.get_allowance("0x29219dd400f2Bf60E5a23d13Be72B486D4038894", "0x9303a680bA1A2924Bb6EeE5A7eD804df2E1824f7")
    crowdfinding_protocol = CrowdfindingProtocol(web3, settings, wallet_address)
    tx_hash_approve = "It's already approved"
    tx_status_approve = "It's already approved"
    if allowance < amount:
        tx_hash_approve, tx_status_approve = token_protocol.approve(
            token_address="0x29219dd400f2Bf60E5a23d13Be72B486D4038894",
            spender_address="0x9303a680bA1A2924Bb6EeE5A7eD804df2E1824f7",
            amount=amount
        )
    tx_hash, tx_status = crowdfinding_protocol.make_contribution(
        amount=amount
    )
    return (f'Transaction crowdfinding contract = tx_hash: {tx_hash}, status tx to crowdfinding : {tx_status}, approve tx = {tx_hash_approve}, status tx approve: {tx_status_approve}')
