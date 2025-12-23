import os
from collections.abc import Callable

import pytest
from _pytest.fixtures import SubRequest
from phuongpv_blog_api_client import AuthenticatedClient, Client, models
from phuongpv_blog_api_client.api.auth import auth_login_create
from selenium.webdriver.remote.webdriver import WebDriver

from plugins.selenium_plugin.cache_decorators import get_cache_name

from pages.auth import SignInPage
from pages.base_pages import BlogPage

pytest_plugins = ("plugins.selenium_plugin.plugin",)


@pytest.fixture(scope="session")
def phuongpv_api_client(request: SubRequest, worker_id: str) -> AuthenticatedClient:
    """Prepare authenticated phuongpv client for sdk."""
    token_cache = get_cache_name(request, "token")
    token = request.config.cache.get(token_cache, None)  # type: ignore

    if not request.config.getoption("--use-cache") or not token:
        token = auth_login_create.sync(
            client=Client(f"{os.environ['APP_BASE_URL']}"),  # type: ignore
            body=models.AuthTokenRequest(
                email=os.environ["SUPER_USER_EMAIL"],
                password=os.environ["SUPER_USER_PASSWORD"],
            ),
        )
        if not isinstance(token, models.Token):
            raise ValueError(f"Failed to get a token. Got: {token}")
        token = token.token

    request.config.cache.set(token_cache, token)  # type: ignore

    return AuthenticatedClient(
        base_url=os.environ["APP_BASE_URL"],
        prefix="token",
        token=token,
        raise_on_unexpected_status=True,
    )


@pytest.fixture
def webdriver(
    request: SubRequest,
    webdriver_getter: Callable[..., WebDriver],
) -> WebDriver:
    """Initialize webdriver for unauthorized session."""
    return webdriver_getter(request)


@pytest.fixture(scope="session")
def superuser_webdriver(
    request: SubRequest,
    webdriver_getter: Callable[..., WebDriver],
) -> WebDriver:
    """Initialize webdriver for `super user` session."""
    webdriver = webdriver_getter(request)
    blog_page = SignInPage.open(webdriver).sign_in(
        username=os.environ["SUPER_USER_USERNAME"],
        password=os.environ["SUPER_USER_PASSWORD"],
    )
    assert isinstance(blog_page, BlogPage)
    return webdriver


@pytest.fixture
def blog_page(superuser_webdriver: WebDriver) -> BlogPage:
    """Initialize blog main page for superuser."""
    return BlogPage.open(superuser_webdriver)
