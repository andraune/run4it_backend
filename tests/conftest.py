"""Defines fixtures available to all tests.
Test framework expects this file to be called conftest.py"""

import pytest

from run4it.app.app import create_app
from run4it.app.database import db as _db
from run4it.app.config import TestConfig
from run4it.api.api_v1 import create_api


@pytest.fixture(scope='function')
def app():
    """Application configured for tests"""
    _app = create_app(TestConfig, __name__)

    with _app.app_context():
        _db.create_all()

    ctx = _app.test_request_context()
    ctx.push()

    yield _app
    ctx.pop()


@pytest.fixture(scope='function')
def api(app):
    """Configure API"""
    _api = create_api(app)
    yield _api


@pytest.fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.commit()
    _db.session.close()
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Test client"""
    _client = app.test_client()
    yield _client
