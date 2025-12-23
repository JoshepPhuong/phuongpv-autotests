import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.auth import SignInPage


@pytest.fixture
def sign_in_page(webdriver: WebDriver) -> SignInPage:
    """Initialize sign in page."""
    return SignInPage.open(webdriver)
