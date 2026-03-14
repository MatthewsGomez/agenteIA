"""
Patch strands.tool before any test collection so tools.py can be imported
without triggering network calls or heavy model loading.
"""
import sys
from unittest.mock import MagicMock

# Replace the entire strands module with a lightweight stub
strands_stub = MagicMock()
strands_stub.tool = lambda fn: fn  # @tool becomes a no-op decorator

sys.modules.setdefault("strands", strands_stub)
sys.modules.setdefault("strands_tools", MagicMock())
