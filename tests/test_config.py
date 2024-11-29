import pytest
from src.config import config


def test_config_exists():
    assert config is not None
