from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from pomcorn import Element, Page, locators

from selenium.webdriver.remote.webdriver import WebDriver


class BlogPage(Page):
    """Page for setting the basic parameters of pomcorn."""

    APP_ROOT = os.environ["APP_ROOT"]

    # Nav bar elements
    sign_in_button = Element(
        locator=locators.ElementWithTextLocator(text="Login", element="a"),
    )
    profile_button = Element(
        locator=locators.ElementWithTextLocator(text="Profile", element="a"),
    )
    create_post_button = Element(
        locator=locators.ElementWithTextLocator(text="Create Post", element="a"),
    )

    def __init__(
        self,
        webdriver: WebDriver,
        *args,
        app_root: str = APP_ROOT,
        wait_timeout: int = int(os.environ.get("BROWSER_WAIT", 5)),
        poll_frequency: float = float(os.environ.get("BROWSER_POLL_FREQUENCY", 0.01)),
        **kwargs,
    ) -> None:
        super().__init__(
            webdriver,
            app_root=app_root,
            wait_timeout=wait_timeout,
            poll_frequency=poll_frequency,
        )

    @contextmanager
    def wait_for_url_change(self) -> Iterator[None]:
        """Context manager for interacting with page switching."""
        old_url = self.current_url
        yield
        self.wait_until_url_changes(old_url)
