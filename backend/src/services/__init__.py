"""Services package.

Avoid importing submodules at package import time to prevent unnecessary
side-effects (e.g., requiring optional dependencies for unrelated scripts).
"""

__all__ = []
