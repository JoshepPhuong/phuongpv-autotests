import os
from collections.abc import Callable
from typing import TypeVar

import tenacity
from selenium.common.exceptions import WebDriverException

R = TypeVar("R")


def retry(func: Callable[..., R]) -> Callable[..., R]:
    """Shortcut for retrying various selenium actions.

    This is just wrapper for `@tenacity.retry` that retries common selenium webdriver exceptions
    like `StaleElementReferenceException`, `ElementNotInteractableException`, etc

    """
    decorator = tenacity.retry(
        stop=tenacity.stop_after_attempt(int(os.environ.get("MAX_RETRY_ATTEMPTS", 3))),
        wait=tenacity.wait_exponential(min=1),
        reraise=True,
        retry=tenacity.retry_if_exception_type(WebDriverException),
    )
    return decorator(func)
