from pomcorn import Element, locators

from phuongpv_blog_api_client import models
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_pages import BlogPage
from pages.caching import memoize_open
from pages.common import fields

from .post_details_page import PostDetailsPage


class PostCreatePage(BlogPage):
    """Represent Create Post page of PhuongPV Blog."""

    title = fields.Input("Title")
    description = fields.TextArea("Description")
    content = fields.TextArea("Content")
    publish_button = Element(locator=locators.ButtonWithTextLocator("Post"))

    @classmethod
    @memoize_open
    def open(cls, webdriver: WebDriver) -> "PostCreatePage":
        """Open Create Post page and initialize page object."""
        blog_page = BlogPage.open(webdriver)
        blog_page.create_post_button.click()
        return cls(webdriver)

    def check_page_is_loaded(self) -> bool:
        return self.title.body.is_displayed

    def create(self, post: models.Post) -> PostDetailsPage:
        """Create a new blog post."""
        self.title.fill(post.title)
        self.description.fill(post.description)
        self.content.fill(post.content)
        with self.wait_for_url_change():
            self.publish_button.click()
        return PostDetailsPage(self.webdriver, post)
