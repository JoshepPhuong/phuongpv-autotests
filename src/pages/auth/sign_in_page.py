from pomcorn import Element, locators

from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_pages import BlogPage
from pages.caching import memoize_open

from .profile_page import ProfilePage


class SignInPage(BlogPage):
    """Represent Sign In page of PhuongPV Blog."""

    username = Element(locator=locators.IdLocator("id_username"))
    password = Element(locator=locators.IdLocator("id_password"))
    login_button = Element(locator=locators.ButtonWithTextLocator("Login"))

    @classmethod
    @memoize_open
    def open(cls, webdriver: WebDriver) -> "SignInPage":
        """Open Sign In page and initialize page object."""
        page = BlogPage.open(webdriver)
        page.sign_in_button.click()
        return cls(webdriver)

    def sign_in(self, username: str, password: str) -> ProfilePage:
        """Sign in to the blog admin panel."""
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
        return ProfilePage(self.webdriver)
