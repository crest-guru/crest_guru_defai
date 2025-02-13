from typing import Dict, Any, Type
from .base import BaseProtocol
from .token import TokenProtocol
from .silo import SiloProtocol
import inspect

class ProtocolRegistry:
    """Registry for all protocol methods"""
    
    # mapping action -> Protocol class
    _protocols: Dict[str, Dict[str, Any]] = {
        "approve": {
            "class": TokenProtocol,
            "method": "approve"
        },
        "silo_withdraw": {
            "class": SiloProtocol,
            "method": "withdraw"
        },
        "silo_deposit_native": {
            "class": SiloProtocol,
            "method": "deposit_native"
        }
    }

    @classmethod
    def get_all_methods(cls) -> Dict[str, Any]:
        """Get information about all registered methods"""
        methods = {}
        for action, protocol in cls._protocols.items():
            methods[action] = cls._get_method_info(protocol, action)
        return methods

    @classmethod
    def _get_method_info(cls, protocol_info: Dict[str, Any], action: str) -> Dict[str, Any]:
        """Extract method information using reflection"""
        method = getattr(protocol_info["class"], protocol_info["method"])
        
        # get method signature
        signature = inspect.signature(method)
        
        return {
            "description": method.__doc__,
            "params": {
                name: {
                    "type": str(param.annotation),
                    "default": None if param.default == param.empty else str(param.default),
                    "required": param.default == param.empty
                }
                for name, param in signature.parameters.items()
                if name not in ['self']
            }
        }

    @classmethod
    def get_protocol(cls, action: str) -> Type[BaseProtocol]:
        """Get protocol class by action"""
        if action not in cls._protocols:
            raise ValueError(f"Unknown action: {action}")
        return cls._protocols[action]["class"]

    @classmethod
    def get_protocol_info(cls, action: str) -> Dict[str, Any]:
        """Get protocol class and method by action"""
        if action not in cls._protocols:
            raise ValueError(f"Unknown action: {action}")
        return cls._protocols[action] 