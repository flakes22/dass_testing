"""Pytest configuration for integration tests."""

from pathlib import Path
import sys


# Ensure imports like `from core...` resolve to integration/code/*.
CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
