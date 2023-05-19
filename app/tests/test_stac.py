import os
from dotenv import load_dotenv
from unittest.mock import Mock, patch

from app.main import app
from app.core.db.session import Base

load_dotenv(".env")

client = test_client()
ENDPOINT = "/stac/"


def test_get_stac():

    """
    Tests if the stac get request is successfull
    """

    response = client.get(ENDPOINT)
    assert response.status_code == 200
