import functools
import logging
import mimetypes
import os
import pathlib
import socket
import typing
from collections.abc import Callable
from enum import StrEnum

import pytest
from _pytest.fixtures import SubRequest
from _pytest.scope import _ALL_SCOPES, Scope
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions, BaseOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class SupportedBrowsers(StrEnum):
    """Available browsers for remote webdriver."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    MICROSOFT_EDGE = "MicrosoftEdge"
    # Short name for MicrosoftEdge browser allows use same name as selenium image
    EDGE = "edge"


SUPPORTED_WEBDRIVERS: dict[SupportedBrowsers, type[WebDriver]] = {
    SupportedBrowsers.CHROME: selenium_webdriver.Chrome,
    SupportedBrowsers.FIREFOX: selenium_webdriver.Firefox,
    SupportedBrowsers.EDGE: selenium_webdriver.ChromiumEdge,
    SupportedBrowsers.MICROSOFT_EDGE: selenium_webdriver.ChromiumEdge,
}


class WidthHeight(typing.NamedTuple):
    """Class for storing WebDriver width and height arguments."""

    width: str
    height: str


class SeleniumPlugin:
    """A mixture of original selenium plugin and factory logic from splinter plugin."""

    LOGGER = logging.getLogger(__name__)
    LOCALE = "en, en_US"
    LOGGING_PREFERENCES = {
        "browser": "ALL",
        "driver": "ALL",
    }
    SELENOID_CAPABILITIES = {
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": False,
            "enableLog": False,
            "name": (
                "Created by "
                f"{os.getenv('RUN_SOURCE_URL', socket.gethostname())}"  # cspell:disable-line
            ),
        },
    }

    # spell-checker:disable
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(
        self,
        items: list[pytest.Function],
    ) -> None:
        """Sort tests in way that tests with function scoped webdriver will be first."""

        def item_comparator(item: pytest.Function) -> int:
            for fixture_defs in item._fixtureinfo.name2fixturedefs.values():
                for fixture in fixture_defs:
                    if fixture.argname.endswith("webdriver"):
                        # See docstring of `Scope` to find description of scopes order
                        return _ALL_SCOPES.index(Scope(fixture.scope))
            return 0

        items.sort(key=item_comparator)

    # spell-checker:enable

    @pytest.fixture(scope="session")
    def webdriver_name(self, request: SubRequest) -> SupportedBrowsers:
        raw_browser_name = request.config.getoption("--webdriver")
        browser_name = SupportedBrowsers(raw_browser_name)
        if browser_name == SupportedBrowsers.EDGE:
            return SupportedBrowsers.MICROSOFT_EDGE
        return browser_name

    @pytest.fixture(scope="session")
    def window_size(self, request: SubRequest) -> WidthHeight:
        width, height = request.config.getoption("--webdriver-window-size").split(",")
        return WidthHeight(width, height)

    @pytest.fixture(scope="session")
    def implicitly_wait(self, request: SubRequest) -> int:
        return int(request.config.getoption("--webdriver-implicitly-wait"))

    @pytest.fixture(scope="session")
    def headless(self, request: SubRequest) -> bool:
        return bool(request.config.getoption("--webdriver-headless"))

    @pytest.fixture(scope="session")
    def remote(self, request: SubRequest) -> bool:
        return bool(request.config.getoption("--webdriver-remote"))

    @pytest.fixture(scope="session")
    def remote_url(self, request: SubRequest) -> str:
        """Get address of remote browser hub."""
        remote_url = request.config.getoption("--webdriver-remote-url")
        if remote_url:
            return remote_url
        return os.environ["REMOTE_BROWSER_ADDR"]

    @pytest.fixture(scope="session")
    def tmp_download_dir(self, tmpdir_factory: pytest.TempdirFactory) -> pathlib.Path:
        """Generate tmp folder for downloaded files."""
        return tmpdir_factory.mktemp("tmp_download_dir")

    @pytest.fixture(scope="session")
    def download_file_types(self) -> str:
        """Mimetypes which firefox will download without asking.

        Comma-separated.

        """
        mimetypes_list = sorted(
            [
                *set(mimetypes.types_map.values()),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ],
        )
        return ",".join(mimetypes_list)

    @pytest.fixture(scope="session")
    def chrome_options(
        self,
        remote: bool,
        headless: bool,
        tmp_download_dir: pathlib.Path,
    ) -> selenium_webdriver.ChromeOptions:
        """Set up chrome settings."""
        chrome_options = selenium_webdriver.ChromeOptions()
        preferences: dict[str, object] = {
            "intl.accept_languages": self.LOCALE,
        }
        if not remote:
            preferences.update(
                **{
                    "download.default_directory": str(tmp_download_dir),
                    "download.directory_upgrade": True,
                },
            )
        chrome_options.add_experimental_option("prefs", preferences)
        chrome_options.set_capability("goog:loggingPrefs", self.LOGGING_PREFERENCES)
        if headless:
            chrome_options.add_argument("--headless=new")
        return chrome_options

    @pytest.fixture(scope="session")
    def firefox_options(
        self,
        remote: bool,
        headless: bool,
        download_file_types: str,
        tmp_download_dir: pathlib.Path,
    ) -> selenium_webdriver.FirefoxOptions:
        """Set up firefox settings."""
        firefox_options = selenium_webdriver.FirefoxOptions()
        firefox_options.set_preference("intl.accept_languages", self.LOCALE)
        firefox_options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            download_file_types,
        )
        firefox_options.set_preference("browser.download.alwaysOpenPanel", False)

        if not remote:
            # 0 means to download to the desktop,
            # 1 means to download to the default "Downloads" directory,
            # 2 means to use the directory
            firefox_options.set_preference("browser.download.folderList", 2)
            firefox_options.set_preference("browser.download.dir", str(tmp_download_dir))
            # To avoid using Firefox's default `use_system_proxy` setting
            firefox_options.set_preference("network.proxy.type", 0)

        if headless:
            firefox_options.add_argument("--headless")

        return firefox_options

    @pytest.fixture(scope="session")
    def edge_options(
        self,
        remote: bool,
        headless: bool,
        tmp_download_dir: pathlib.Path,
    ) -> selenium_webdriver.EdgeOptions:
        """Set up edge settings."""
        options = selenium_webdriver.EdgeOptions()
        preferences: dict[str, object] = {
            "intl.accept_languages": self.LOCALE,
        }
        if not remote:
            preferences.update(
                **{
                    "download.default_directory": str(tmp_download_dir),
                    "download.directory_upgrade": True,
                },
            )
        options.add_experimental_option("prefs", preferences)
        if headless:
            options.add_argument("--headless=new")
        return options

    @pytest.fixture(scope="session")
    def remote_options(self, webdriver_name: SupportedBrowsers) -> ArgOptions:
        """Set options for remote browsers.

        Firefox doesn't work with `loggingPrefs` capability so it's set just for other browsers.

        """
        remote_capabilities = {
            "browserName": webdriver_name,
            **self.SELENOID_CAPABILITIES,
        }

        options = ArgOptions()
        match remote_capabilities["browserName"]:
            case SupportedBrowsers.CHROME:
                options.set_capability("goog:loggingPrefs", self.LOGGING_PREFERENCES)
            case SupportedBrowsers.MICROSOFT_EDGE:
                options.set_capability("ms:loggingPrefs", self.LOGGING_PREFERENCES)
            case _:
                pass

        for key, value in remote_capabilities.items():
            options.set_capability(key, value)

        return options

    @pytest.fixture(scope="session")
    def options(
        self,
        webdriver_name: SupportedBrowsers,
        chrome_options: selenium_webdriver.ChromeOptions,
        firefox_options: selenium_webdriver.FirefoxOptions,
        edge_options: selenium_webdriver.EdgeOptions,
        remote_options: ArgOptions,
        remote: bool,
    ) -> BaseOptions:
        """Browser options.

        By default return chrome options.

        """
        if remote:
            return remote_options

        if webdriver_name == SupportedBrowsers.FIREFOX:
            return firefox_options

        if webdriver_name in (SupportedBrowsers.EDGE, SupportedBrowsers.MICROSOFT_EDGE):
            return edge_options

        return chrome_options

    @pytest.fixture(scope="session")
    def driver_class(self, webdriver_name: SupportedBrowsers, remote: bool) -> type[WebDriver]:
        """Get webdriver_name class based on cmd arg."""
        if remote:
            return selenium_webdriver.Remote
        return SUPPORTED_WEBDRIVERS[webdriver_name]

    @pytest.fixture(scope="session")
    def driver_kwargs(
        self,
        remote_url: str,
        options: BaseOptions,
        remote: bool,
    ) -> dict[str, typing.Any]:
        """Set up kwargs for webdriver class init."""
        kwargs: dict[str, typing.Any] = {"options": options}
        if remote:
            kwargs["command_executor"] = remote_url
        return kwargs

    @pytest.fixture(scope="session")
    def webdriver_getter(
        self,
        webdriver_name: SupportedBrowsers,
        driver_class: type[selenium_webdriver.Remote],
        driver_kwargs: dict[str, typing.Any],
        window_size: WidthHeight,
        implicitly_wait: int,
    ) -> Callable[..., WebDriver]:
        """Fixture for webdriver."""
        return functools.partial(
            self.webdriver_factory,
            webdriver_name=webdriver_name,
            driver_class=driver_class,
            driver_kwargs=driver_kwargs,
            window_size=window_size,
            implicitly_wait=implicitly_wait,
        )

    def webdriver_factory(
        self,
        request: SubRequest,
        webdriver_name: SupportedBrowsers,
        driver_class: type[selenium_webdriver.Remote],
        driver_kwargs: dict[str, typing.Any],
        window_size: WidthHeight,
        implicitly_wait: int,
    ) -> WebDriver:
        """Return a WebDriver instance based on capabilities."""
        webdriver = driver_class(**driver_kwargs)
        webdriver.set_window_size(*window_size)
        webdriver.implicitly_wait(implicitly_wait)

        request.node._webdriver = webdriver
        request.addfinalizer(webdriver.quit)

        if webdriver_name == SupportedBrowsers.MICROSOFT_EDGE:
            # Edge browser open Office files in new tab by default
            # so we disabling this feature below
            webdriver.get("edge://settings/downloads")
            WebDriverWait(webdriver, timeout=20).until(
                expected_conditions.visibility_of_element_located(
                    locator=(By.XPATH, "//input[@aria-label='Open Office files in the browser']"),
                ),
            ).click()

            # TODO: Remove after this is fixed in Edge next version (above 119)
            # Starting with Edge 119, open downloads menu is considered a separate webdriver window,
            # and sometimes tests are run in it and fail. So we have disabled opening of this window
            WebDriverWait(webdriver, timeout=20).until(
                expected_conditions.visibility_of_element_located(
                    locator=(By.XPATH, "//input[contains(@aria-label, 'Show downloads menu')]"),
                ),
            ).click()

        webdriver.maximize_window()
        return webdriver

    @pytest.fixture(autouse=True)
    def annotate_node_with_driver(self, request: SubRequest) -> None:
        """Add webdriver instance to test, that later will be used to generate debug info.

        This fixture detects whether a test or its parent is using a selenium webdriver, and marks
        the node with the webdriver instance.

        """
        for fixture_name in request.fixturenames:  # cspell:disable-line
            if fixture_name.endswith("webdriver") and isinstance(
                request.getfixturevalue(fixture_name),
                selenium_webdriver.Remote,
            ):
                request.node._webdriver = request.getfixturevalue(fixture_name)
