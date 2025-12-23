import pytest

from pages.base_pages import BlogPage
from pages.posts.post_create_page import PostCreatePage


@pytest.fixture
def post_create_page(blog_page: BlogPage) -> PostCreatePage:
    """Initialize Create Post page for superuser."""
    blog_page.create_post_button.click()
    return PostCreatePage(blog_page.webdriver)
