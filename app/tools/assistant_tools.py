import os
import json
from importlib import import_module
from typing import Dict, Any

class ToolRegistry:
    def __init__(self):
        self.tools_config = []
        self.tools_functions = {}
        self._load_all_tools()

    def _load_tool_configs(self) -> None:
        """Loads all tool configurations from JSON files"""
        configs_dir = os.path.join(os.path.dirname(__file__), 'configs')
        for filename in os.listdir(configs_dir):
            if filename.endswith('.json'):
                with open(os.path.join(configs_dir, filename)) as f:
                    config = json.load(f)
                    self.tools_config.extend(config.values())

    def _load_tool_functions(self) -> None:
        """Imports all functions from modules in the functions directory"""
        functions_dir = os.path.join(os.path.dirname(__file__), 'functions')
        for filename in os.listdir(functions_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                module = import_module(f'.functions.{module_name}', package='app.tools')
                
                
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        self.tools_functions[attr_name] = attr

    def _load_all_tools(self) -> None:
        """Loads all configurations and functions"""
        self._load_tool_configs()
        self._load_tool_functions()

    @property
    def configs(self) -> list:
        return self.tools_config

    @property
    def functions(self) -> Dict[str, Any]:
        return self.tools_functions

tool_registry = ToolRegistry()