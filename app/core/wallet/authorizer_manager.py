from web3 import Web3
from eth_account import Account
from pathlib import Path
import os
import json
from config.settings import Settings
from app.core.wallet.safe_wallet import SafeWallet
from config.initial_address_setup import INITIAL_CONTRACTS, INITIAL_SPENDERS, INITIAL_SILOS
from app.db.database import get_wallet 

class AuthorizerManager:
    """Manager for Cobo Argus authorizers"""
    
    def __init__(self, web3: Web3, settings: Settings):
        self.web3 = web3
        self.settings = settings
        self.helper_contract = self._get_contract(
            settings.ARGUS_HELPER_ADDRESS, 
            "ArgusAccountHelper"
        )
        
        
        self.authorizer_implementations = {
            "ApproveAuthorizerV2": settings.APPROVE_AUTHORIZER_IMPL,
            "SiloAuthorizer": settings.SILO_AUTHORIZER_IMPL
        }

    def create_authorizer(
        self, 
        cobo_address: str, 
        user_address: str,  
        authorizer_type: str = "ApproveAuthorizerV2",
        role_name: str = "agent"
    ) -> str:
        """Create new authorizer for Cobo
        
        Args:
            cobo_address: Address of Cobo Argus
            user_address: Address of user (for agent setup)
            authorizer_type: Type of authorizer (from implementations map)
            
        Returns:
            str: Address of created authorizer
        """
        
        try:
            impl_address = self.authorizer_implementations.get(authorizer_type)
            if not impl_address:
                raise ValueError(f"Unknown authorizer type: {authorizer_type}")
            
            
            name_abi = [{
                "inputs": [],
                "name": "NAME",
                "outputs": [{"type": "bytes32"}],
                "stateMutability": "view",
                "type": "function"
            }]
            
            impl_contract = self.web3.eth.contract(address=impl_address, abi=name_abi)
            authorizer_name = impl_contract.functions.NAME().call()
            
            
            current_block = self.web3.eth.block_number
            name_bytes = authorizer_name[:28]  
            block_bytes = current_block.to_bytes(4, 'big')
            tag = name_bytes + block_bytes
            
            
            
            
            safe_address = self._get_safe_address_from_cobo(cobo_address)
            safe = SafeWallet(self.web3, self.settings, safe_address)
            
            init_data = self.helper_contract.encode_abi(
                "createAuthorizer",
                args=[self.settings.COBO_FACTORY_ADDRESS, cobo_address, f"0x{authorizer_name.hex()}", tag]
            )
            
            tx_hash = safe.execute_transaction(
                to=self.settings.ARGUS_HELPER_ADDRESS,
                data=init_data,
                operation=1  # DelegateCall
            )
            
            
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            authorizer_address = self._get_proxy_address_from_receipt(receipt)
            print(f"Found authorizer proxy at: {authorizer_address}")
            
            
            self.setup_roles(user_address, safe_address, cobo_address, authorizer_address, role_name)
            
            if authorizer_type == "ApproveAuthorizerV2":
                self.setup_approve_list_manager(safe_address, authorizer_address)
                
                self.setup_initial_addresses(authorizer_address)
                
                self.transfer_approve_list_manager(safe_address, authorizer_address, user_address)

            elif authorizer_type == "SiloAuthorizer":
                self.transfer_silo_admin(safe_address, authorizer_address, self.settings.DEPLOYER_ADDRESS)
                self.setup_silo_markets(safe_address, authorizer_address)
                self.transfer_silo_admin(safe_address, authorizer_address, user_address)
            
            return authorizer_address
        
        except Exception as e:
            print(f"Error creating authorizer: {str(e)}")
            raise

    def setup_roles(
        self,
        user_address: str,      # user address for getting agent
        safe_address: str,      # safe address
        cobo_address: str,      # cobo address
        authorizer_address: str,  # authorizer address
        role_name: str
    ):
        """Setup roles for authorizer"""
        
        wallet_data = get_wallet(user_address) 
        agent_address = wallet_data['agent_address']
        
        role_bytes = self.web3.to_bytes(text=role_name).ljust(32, b'\0')
        role_names = [role_bytes]
        
        transactions = [
            self.build_add_roles_tx(cobo_address, role_names),
            self.build_add_authorizer_tx(cobo_address, authorizer_address, role_names),
            self.build_grant_roles_tx(cobo_address, role_names, agent_address)
        ]
        
        self._send_multisend_tx(safe_address, transactions)

    def _build_create_tx(self, cobo_address: str, name: str, tag: bytes) -> dict:
        """Build transaction for creating authorizer"""
        init_data = self.helper_contract.encode_abi(
            "createAuthorizer",
            args=[self.settings.COBO_FACTORY_ADDRESS, cobo_address, name, tag]
        )
        
        return {
            'from': self.settings.DEPLOYER_ADDRESS,
            'to': self.settings.ARGUS_HELPER_ADDRESS,
            'data': init_data,
            'gas': 2000000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        }

    def _send_transaction(self, tx: dict) -> dict:
        """Send and wait for transaction"""
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def _get_proxy_address_from_receipt(self, receipt: dict) -> str:
        """Get proxy address from ProxyCreated event"""
        PROXY_CREATED_TOPIC = "532cf4635ae9ff4e1e42ba14917e825d00f602f28297cc654fa3b414b911232b"
        
        for log in receipt['logs']:
            if log['topics'][0].hex().lower() == PROXY_CREATED_TOPIC.lower():
                raw_address = "0x" + log['data'].hex()[-40:]
                return self.web3.to_checksum_address(raw_address)
                
        raise Exception("ProxyCreated event not found in receipt")

    def _get_contract(self, address: str, name: str):
        """Get contract instance"""
        abi_path = os.path.join(Path(__file__).parent.parent.parent, "abi", f"{name}.json")
        with open(abi_path, "r") as f:
            contract_abi = json.load(f)
        return self.web3.eth.contract(address=address, abi=contract_abi)

    def build_add_roles_tx(self, cobo_address: str, role_names: list) -> bytes:
        """Build transaction data for adding roles"""
        cobo_contract = self._get_contract(cobo_address, "CoboSafeAccount")
        role_manager_address = cobo_contract.functions.roleManager().call()
        
        role_manager = self._get_contract(role_manager_address, "RoleManager")
        tx_data = role_manager.encode_abi("addRoles", args=[role_names])
        
        if isinstance(tx_data, str) and tx_data.startswith('0x'):
            tx_data = bytes.fromhex(tx_data[2:])
        
        operation = 0  # CALL
        address = bytes.fromhex(role_manager_address[2:])
        value = (0).to_bytes(32, 'big')
        data_length = len(tx_data).to_bytes(32, 'big')
        
        return b''.join([operation.to_bytes(1, 'big'), address, value, data_length, tx_data])

    def build_add_authorizer_tx(self, cobo_address: str, authorizer_address: str, role_names: list) -> bytes:
        """Build transaction data for adding authorizer"""
        tx_data = self.helper_contract.encode_abi(
            "addAuthorizer",
            args=[cobo_address, authorizer_address, False, role_names]
        )
        
        if isinstance(tx_data, str) and tx_data.startswith('0x'):
            tx_data = bytes.fromhex(tx_data[2:])
        
        operation = 1  # DELEGATECALL
        address = bytes.fromhex(self.settings.ARGUS_HELPER_ADDRESS[2:])
        value = (0).to_bytes(32, 'big')
        data_length = len(tx_data).to_bytes(32, 'big')
        
        return b''.join([operation.to_bytes(1, 'big'), address, value, data_length, tx_data])

    def build_grant_roles_tx(self, cobo_address: str, role_names: list, agent_address: str) -> bytes:
        """Build transaction data for granting roles"""
        tx_data = self.helper_contract.encode_abi(
            "grantRoles",
            args=[cobo_address, role_names, [agent_address]]
        )
        
        if isinstance(tx_data, str) and tx_data.startswith('0x'):
            tx_data = bytes.fromhex(tx_data[2:])
        
        operation = 1  # DELEGATECALL
        address = bytes.fromhex(self.settings.ARGUS_HELPER_ADDRESS[2:])
        value = (0).to_bytes(32, 'big')
        data_length = len(tx_data).to_bytes(32, 'big')
        
        return b''.join([operation.to_bytes(1, 'big'), address, value, data_length, tx_data])

    def _send_multisend_tx(self, safe_address: str, transactions: list) -> dict:
        """Send transactions through MultiSend"""
        multi_send_data = b''.join(transactions)
        
        multisend_contract = self._get_contract(
            self.settings.MULTISEND_ADDRESS,
            "MultiSend"
        )
        
        multi_tx_data = multisend_contract.encode_abi(
            "multiSend",
            args=[multi_send_data]
        )
        
        safe = SafeWallet(self.web3, self.settings, safe_address)
        tx_hash = safe.execute_transaction(
            to=self.settings.MULTISEND_ADDRESS,
            data=multi_tx_data,
            operation=1  # DelegateCall
        )
        
        
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def setup_approve_list_manager(self, safe_address: str, authorizer_address: str) -> None:
        """Setup approve list manager for authorizer
        
        Args:
            safe_address: Address of Safe wallet
            authorizer_address: Address of authorizer
        """
        authorizer_contract = self._get_contract(authorizer_address, "ApproveAuthorizerV2")
        
        tx_data = authorizer_contract.encode_abi(
            "setApproveListManager",
            args=[self.settings.DEPLOYER_ADDRESS]
        )
        
        safe = SafeWallet(self.web3, self.settings, safe_address)
        tx_hash = safe.execute_transaction(
            to=authorizer_address,
            data=tx_data,
            operation=0  # Call
        )
        

    def _get_safe_address_from_cobo(self, cobo_address: str) -> str:
        """Get Safe address from Cobo contract"""
        cobo_contract = self._get_contract(cobo_address, "CoboSafeAccount")
        return cobo_contract.functions.safe().call()

    def setup_initial_addresses(self, authorizer_address: str) -> None:
        """Setup initial contracts and spenders for ApproveAuthorizerV2
        
        Args:
            authorizer_address: Address of authorizer
        """
        
        authorizer_contract = self._get_contract(authorizer_address, "ApproveAuthorizerV2")
        
        print("Adding contracts:", INITIAL_CONTRACTS)
        tx_data = authorizer_contract.encode_abi(
            "addContracts",
            args=[INITIAL_CONTRACTS]
        )
        
        tx = {
            'from': self.settings.DEPLOYER_ADDRESS,
            'to': authorizer_address,
            'data': tx_data,
            'gas': 600000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        }
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        tx_data = authorizer_contract.encode_abi(
            "addSpenders",
            args=[INITIAL_SPENDERS]
        )
        
        tx = {
            'from': self.settings.DEPLOYER_ADDRESS,
            'to': authorizer_address,
            'data': tx_data,
            'gas': 600000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        }
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def transfer_approve_list_manager(self, safe_address: str, authorizer_address: str, new_manager: str) -> None:
        """Transfer approve list manager role to new address
        
        Args:
            safe_address: Address of Safe wallet
            authorizer_address: Address of authorizer
            new_manager: Address that will become the new manager
        """
        authorizer_contract = self._get_contract(authorizer_address, "ApproveAuthorizerV2")
        
        tx_data = authorizer_contract.encode_abi(
            "setApproveListManager",
            args=[new_manager]
        )
        
        safe = SafeWallet(self.web3, self.settings, safe_address)
        tx_hash = safe.execute_transaction(
            to=authorizer_address,
            data=tx_data,
            operation=0  # Call
        )
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transferred approve list manager role to {new_manager}")

    

    def transfer_silo_admin(self, safe_address: str, authorizer_address: str, new_admin: str) -> None:
        """Transfer silo admin role to new address"""
        authorizer_contract = self._get_contract(authorizer_address, "SiloAuthorizer")
        
        tx_data = authorizer_contract.encode_abi(
            "setAdmin",
            args=[new_admin]
        )
        
        safe = SafeWallet(self.web3, self.settings, safe_address)
        tx_hash = safe.execute_transaction(
            to=authorizer_address,
            data=tx_data,
            operation=0  # Call
        )
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def setup_silo_markets(self, safe_address: str, authorizer_address: str) -> None:
        authorizer_contract = self._get_contract(authorizer_address, "SiloAuthorizer")
        
        tx_data = authorizer_contract.encode_abi(
            "addPoolAddresses",
            args=[INITIAL_SILOS]
        ) 

        tx = {
            'from': self.settings.DEPLOYER_ADDRESS,
            'to': authorizer_address,
            'data': tx_data,
            'gas': 600000,
            'nonce': self.web3.eth.get_transaction_count(self.settings.DEPLOYER_ADDRESS),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.settings.CHAIN_ID
        }
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.settings.DEPLOYER_PRIVATE_KEY)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Added silo markets: {receipt}")
    