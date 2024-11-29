# tests/conftest.py

import sys
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def add_src_to_sys_path():
    """
    Adds the src directory to sys.path to allow absolute imports from src/.
    This fixture runs automatically for the entire test session.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
