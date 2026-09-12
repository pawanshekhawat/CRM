from typing import Dict, List, Optional
import logging
from app.modules.base_module import BaseModule

logger = logging.getLogger("CRM.ModuleRegistry")

class ModuleRegistry:
    """Central registry holding all pluggable modules."""

    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}

    def register(self, module: BaseModule):
        """Registers a new module."""
        if module.module_id in self._modules:
            logger.warning(f"Module '{module.module_id}' already registered. Overwriting.")
        self._modules[module.module_id] = module
        logger.info(f"Registered module: {module.module_name} [{module.module_id}]")

    def unregister(self, module_id: str):
        if module_id in self._modules:
            del self._modules[module_id]

    def get_module(self, module_id: str) -> Optional[BaseModule]:
        return self._modules.get(module_id)

    def get_all_modules(self) -> List[BaseModule]:
        return sorted(self._modules.values(), key=lambda m: m.sort_order)

    def initialize_all(self):
        for module in self._modules.values():
            try:
                module.initialize()
            except Exception as e:
                logger.error(f"Error initializing module {module.module_id}: {e}", exc_info=True)

    def shutdown_all(self):
        for module in self._modules.values():
            try:
                module.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down module {module.module_id}: {e}", exc_info=True)

# Global singleton module registry
module_registry = ModuleRegistry()
