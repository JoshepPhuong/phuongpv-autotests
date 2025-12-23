import pytest

from .collect_browser_screenshots_plugin import BrowserScreenshotLinkPlugin
from .selenium_plugin import SeleniumPlugin, SupportedBrowsers


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Register uSummit plugins."""
    config.pluginmanager.register(  # cspell:disable-line
        plugin=SeleniumPlugin(),
        name="selenium_plugin",
    )
    collect_screenshot_enabled = config.getoption("--collect-screenshots")
    if collect_screenshot_enabled:
        config.pluginmanager.register(  # cspell:disable-line
            plugin=BrowserScreenshotLinkPlugin(),
            name="collect_screenshot_plugin",
        )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Set up cmd args."""
    # Selenium plugin args
    parser.addoption(
        "--webdriver",
        choices=SupportedBrowsers,
        default=SupportedBrowsers.CHROME,
        help="Specify browser",
    )
    parser.addoption(
        "--webdriver-remote",
        action="store_true",
        default=False,
        help="Run browser on remote machine",
    )
    parser.addoption(
        "--webdriver-headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode",
    )
    parser.addoption(
        "--webdriver-window-size",
        action="store",
        default="1920,1080",
        help="Size of browser window in pixels",
    )
    parser.addoption(
        "--webdriver-implicitly-wait",
        action="store",
        default=2,
        help=(
            "An implicit wait tells WebDriver to poll the DOM for a certain "
            "amount of time when trying to find any element (or elements) not "
            "immediately available in seconds, has to be lower than global "
            "wait parameter"
        ),
    )
    parser.addoption(
        "--webdriver-remote-url",
        help="Url to remote drivers hub",
    )
    # Screenshots collect plugin for jenkins runs
    parser.addoption(
        "--collect-screenshots",
        action="store_true",
        default=False,
        help="Save browser screenshot and add link to logs if test is failed",
    )
    # Use cache feature
    parser.addoption(
        "--use-cache",
        "--uc",
        action="store_true",
        default=False,
        help="Use cache feature",
    )
