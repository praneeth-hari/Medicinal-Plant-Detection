"""
test_auth.py — Tests for the Authentication API endpoints.
============================================================
Covers user registration, login, token refresh, and profile access.
"""

import pytest


class TestAuthAPI:
    """Test suite for /api/v1/auth endpoints."""

    def test_register_user(self):
        """POST /auth/register should create a new user account."""
        # TODO: Implement test
        pass

    def test_register_duplicate_email_returns_400(self):
        """POST /auth/register with existing email should return 400."""
        # TODO: Implement test
        pass

    def test_login_valid_credentials(self):
        """POST /auth/login with valid credentials should return a JWT."""
        # TODO: Implement test
        pass

    def test_login_invalid_credentials_returns_401(self):
        """POST /auth/login with wrong password should return 401."""
        # TODO: Implement test
        pass

    def test_get_current_user(self):
        """GET /auth/me with valid token should return user profile."""
        # TODO: Implement test
        pass

    def test_refresh_token(self):
        """POST /auth/refresh should return a new access token."""
        # TODO: Implement test
        pass
