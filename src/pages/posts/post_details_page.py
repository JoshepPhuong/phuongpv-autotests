from pomcorn import Element, locators

from phuongpv_blog_api_client import models
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_pages import BlogPage
from pages.caching import memoize_open


class PostDetailsPage(BlogPage):
    """Represent Post Details page of PhuongPV Blog."""

    title = Element(locator=locators.ClassLocator("article-title"))
    # Post description and content have the same class name `article-content`,
    # but description is always before content
    description = Element(locator=locators.ClassLocator("article-content"))
    content = Element(locator=locators.ClassLocator("article-content").extend_query("[last()]"))

    def __init__(
        self,
        webdriver: WebDriver,
        post: models.Post,
    ):
        super().__init__(webdriver)
        self.post = post

    @classmethod
    @memoize_open
    def open(cls, webdriver: WebDriver, post: models.Post) -> "PostDetailsPage":
        """Open Post Details page and initialize page object."""
        blog_page = BlogPage.open(webdriver)
        blog_page.init_element(
            locator=locators.ElementWithTextLocator(
                text=post.title,
                element="a",
                exact=True,
            ),
        ).click()
        return cls(webdriver, post)

    def check_page_is_loaded(self) -> bool:
        return self.title.is_displayed
