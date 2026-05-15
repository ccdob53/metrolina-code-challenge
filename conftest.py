import os

import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.metrolinagreenhouses.com"
API_KEY = os.getenv("API_KEY")


@pytest.fixture(scope="module")
def base_url():
    return BASE_URL


@pytest.fixture(scope="module")
def valid_headers():
    return {"apiKey": API_KEY}


@pytest.fixture
def invalid_headers():
    return {"apiKey": "invalid-key"}


@pytest.fixture
def no_headers():
    return {}
