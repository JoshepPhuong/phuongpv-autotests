import os

from pages.auth import SignInPage


def test_successful_login(sign_in_page: SignInPage):
    """Test login with valid credentials."""
    username = os.environ["SUPER_USER_USERNAME"]
    email = os.environ["SUPER_USER_EMAIL"]
    password = os.environ["SUPER_USER_PASSWORD"]
    profile_page = sign_in_page.sign_in(username=username, password=password)
    assert profile_page.username_input.value == username
    assert profile_page.email_input.value == email
