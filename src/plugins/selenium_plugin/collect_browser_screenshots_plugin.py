import base64
import logging
import os
from collections.abc import Generator
from datetime import datetime

import pytest
from _pytest.config import Config
from _pytest.python import Function
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter
from pluggy._result import Result
from selenium.webdriver.remote.webdriver import WebDriver

from plugins.storage import S3FSStorage


class BrowserScreenshotLinkPlugin:
    """Make a browser screenshot and save it on S3 on test failure.

    Add screenshot link to tests result.

    """

    SCREENSHOT_DIR = "jenkins_runs/{env}/{browser}/{item_name}/{screenshot_name}.png"

    def __init__(self) -> None:
        self.browser: str = ""
        self.logger = logging.getLogger(__name__)

    @pytest.hookimpl(trylast=True)
    def pytest_configure(self, config: Config) -> None:
        """Save used browser for run's name and folder name."""
        self.browser = config.getoption("--webdriver")

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)  # cspell:disable-line
    def pytest_terminal_summary(
        self,
        terminalreporter: TerminalReporter,
        exitstatus: int,  # cspell:disable-line
        config: pytest.Config,
    ) -> Generator[None]:
        """Add browser screenshot link to test results."""
        yield
        reports = terminalreporter.getreports("failed")  # cspell:disable-line
        if not reports:
            return
        terminalreporter.write_sep("-", "Browser screenshot links")
        for report in reports:
            try:
                extra_line = report.longrepr.reprtraceback.extraline  # cspell:disable-line
            except AttributeError:
                continue
            if extra_line:
                browser_link = extra_line.split()[-1]
                node_id = report.nodeid
                terminalreporter.write_line(f"{node_id} -> {browser_link}")

    @pytest.hookimpl(hookwrapper=True)  # cspell:disable-line
    def pytest_runtest_makereport(  # cspell:disable-line
        self,
        item: Function,
    ) -> Generator[None]:
        """Redefine pytest hook on test completion.

        At this hook we will add browser screenshot for failed tests.

        """
        provided_report: Result[TestReport] = yield  # type: ignore
        report = provided_report.get_result()
        item_has_webdriver = hasattr(item, "_webdriver")
        if not report.failed or not item_has_webdriver:
            return

        link = self.get_link_to_screenshot(item)
        if not link:
            return

        try:
            message = f"Browser screenshot: {link}"
            report.longrepr.reprtraceback.extraline = message  # type: ignore # cspell:disable-line
            item.user_properties.append(("Browser screenshot", link))
        except AttributeError:
            pass

    def get_link_to_screenshot(self, item: Function) -> str | None:
        """Try to upload screenshot to S3 and get link."""
        screenshot = self.get_screenshot(item._webdriver)  # type: ignore
        if not screenshot:
            return None

        browser_screenshot = base64.b64decode(screenshot)

        filename = self.SCREENSHOT_DIR.format(
            env=os.environ.get("ENVIRONMENT"),
            browser=self.browser,
            item_name=item.name,
            screenshot_name=f"failed_{datetime.today().strftime('%d-%m-%Y_%H:%M')}",
        )

        return self.save_screenshot(browser_screenshot, filename)

    def get_screenshot(self, webdriver: WebDriver) -> bytes | None:
        """Try to get screenshot from browser, simply return `None` in case of errors."""
        try:
            return webdriver.get_screenshot_as_base64().encode("utf-8")
        except Exception:
            self.logger.error(msg="Can't get browser screenshot", exc_info=True)

    def save_screenshot(self, browser_screenshot: bytes, filename: str) -> str | None:
        """Try to save screenshot to S3, simply return `None` in case of errors."""
        try:
            return S3FSStorage().save_file_obj(
                browser_screenshot,
                filename=filename,
                ContentType="image/png",
            )
        except Exception:
            self.logger.error(msg="Can't save screenshot to S3", exc_info=True)
