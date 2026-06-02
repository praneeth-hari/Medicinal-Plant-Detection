"""
conftest.py — Shared Pytest Fixtures
============================================================
This module provides shared fixtures used across all test modules.
"""

import pytest


# ----- Test Database Fixture -----
@pytest.fixture
def test_db():
    """
    Provide a clean test database session.

    Sets up an in-memory SQLite database, creates all tables,
    yields a session, and tears down after the test.
    """
    # TODO: Set up test database engine and session
    yield None  # Replace with actual db session


# ----- Async HTTP Client Fixture -----
@pytest.fixture
def async_client():
    """
    Provide an async HTTP test client for the FastAPI application.

    Uses httpx.AsyncClient with the app's TestClient to make
    requests without starting a real server.
    """
    # TODO: Set up async test client with TestClient
    yield None  # Replace with actual async client


# ----- Test User Fixture -----
@pytest.fixture
def test_user(test_db):
    """
    Create and return a test user in the database.

    Returns a dictionary with user credentials and the created
    user object for use in authenticated test requests.
    """
    # TODO: Create a test user in the test database
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser",
    }


# ----- Auth Headers Fixture -----
@pytest.fixture
def auth_headers(test_user):
    """
    Return authorization headers with a valid JWT for the test user.
    """
    # TODO: Generate a JWT token for the test user
    return {"Authorization": "Bearer <test-token>"}
