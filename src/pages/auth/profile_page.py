from pomcorn import Element, locators

from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_pages import BlogPage
from pages.caching import memoize_open
from pages.common import fields


class ProfilePage(BlogPage):
    """Represent Profile page of PhuongPV Blog."""

    first_name_input = fields.Input(field_label="First Name")
    last_name_input = fields.Input(field_label="Last Name")
    username_input = fields.Input(field_label="Username")
    email_input = fields.Input(field_label="Email")
    save_button = Element(locator=locators.ButtonWithTextLocator("Update"))

    @classmethod
    @memoize_open
    def open(cls, webdriver: WebDriver) -> "ProfilePage":
        """Open Profile page and initialize page object."""
        blog_page = BlogPage.open(webdriver)
        if not blog_page.profile_button.is_displayed:
            raise ValueError(
                "User is not signed in. Please sign in first.",
            )
        blog_page.profile_button.click()
        return cls(webdriver)
