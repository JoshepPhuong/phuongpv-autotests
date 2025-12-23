from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import NewType, ParamSpec, TypeAlias, TypeVar

from pomcorn import Page

from selenium.webdriver.remote.webdriver import WebDriver

PageObject = TypeVar("PageObject", bound=Page)
OpenParams = ParamSpec("OpenParams")

# `PageCacheKey` is new type for a string that includes all data passed to `open` method of page.
# For more information about preparing a page cache key, see `get_page_cache_key` below.
PageCacheKey = NewType("PageCacheKey", str)
PageUrl: TypeAlias = str

# Cached page urls for use in `memoize_open()`
URLS_CACHE: dict[PageCacheKey, PageUrl] = {}


def memoize_open(
    page_open_method: Callable[OpenParams, PageObject],
) -> Callable[OpenParams, PageObject]:
    """Open page for the first time using UI, for subsequent calls use stored URL.

    Cache is based on page class name and params for opening.

    Usage:

    class ProfilePage(BlogPage):

        @classmethod
        @memoize_open
        def open(
            cls,
            webdriver: WebDriver,
        ) -> ProfilePage:
            BlogPage.open(webdriver).profile_button.click()
            return cls(webdriver)

    """

    @wraps(page_open_method)
    def inner(
        cls,  # noqa: ANN001
        webdriver: WebDriver,
        *args: OpenParams.args,
        **kwargs: OpenParams.kwargs,
    ) -> PageObject:
        cache_key = get_page_cache_key(cls, webdriver, args, kwargs)

        # Open page by cached url
        if cache_key in URLS_CACHE:
            stored_url = URLS_CACHE[cache_key]
            webdriver.get(stored_url)
            return cls(webdriver, *args, **kwargs)

        # Open page manually (step-by-step) and save url
        opened_page: PageObject = page_open_method(cls, webdriver, *args, **kwargs)  # type: ignore

        URLS_CACHE[cache_key] = opened_page.current_url
        return opened_page

    return inner  # type: ignore


def get_page_cache_key(
    cls: type[object],
    webdriver: WebDriver,
    *args,
    **kwargs,
) -> PageCacheKey:
    """Generate page cache key based on passed params.

    Key contains page class name, webdriver session id and args/kwargs which passed to page `open`
    method.

    All args/kwargs params are converting to single string because they can include API Models which
    has unhashable type. Also kwargs have unhashable `dict` type by default.

    We have to include the webdriver session ID in cache key, because in some test cases we need
    to reopen the page using the UI (For example, to open it by another user). And for it we will
    create new webdriver session.

    """
    return PageCacheKey(f"""
        PageCacheKey(
            page_class=`{cls.__name__}`,
            webdriver_session_id=`{webdriver.session_id}`,
            args={args},
            kwargs={kwargs},
        )
    """)
