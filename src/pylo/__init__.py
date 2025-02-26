# src/pylo/__init__.py
from .logger import get_logger

# Fixes any Ruff or Pyright warnings
# due to not using the import
__all__ = ["get_logger"]
