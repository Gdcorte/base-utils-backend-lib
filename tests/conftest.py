import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Load test environment variables"""
    load_dotenv(".env.test", override=True)

    yield
