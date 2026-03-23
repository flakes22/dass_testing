"""Auto-bootstrap import paths for direct test script execution.

Python automatically imports `sitecustomize` (if present on sys.path) during
startup. Since these tests are often run directly from `integration/tests`,
we add `integration/code` to sys.path so imports like `from core...` resolve.
"""

from pathlib import Path
import sys


TESTS_DIR = Path(__file__).resolve().parent
CODE_DIR = TESTS_DIR.parent / "code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
