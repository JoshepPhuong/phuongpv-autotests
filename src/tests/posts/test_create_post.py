import pytest
from phuongpv_blog_api_client import AuthenticatedClient, models
from slugify import slugify

import api
from api_factories.utils import generate_name_with_uuid

from pages.posts.post_create_page import PostCreatePage


@pytest.fixture
def post() -> models.Post:
    """Provide a sample blog post data."""
    return models.Post(
        title=generate_name_with_uuid("Blog Post"),
        description="Blog post description.",
        content="Blog post content.",
    )


def test_create_post(
    phuongpv_api_client: AuthenticatedClient,
    post: models.Post,
    post_create_page: PostCreatePage,
):
    """Ensure admin can create post with expected content."""
    post_details_page = post_create_page.create(post)

    # Check API data
    created_post = api.get_post_by_name(phuongpv_api_client, post.title)
    assert created_post

    # Check UI data
    assert post_details_page.title.get_text() == post.title
    assert post_details_page.description.get_text() == post.description
    assert post_details_page.content.get_text() == post.content
    assert slugify(post.title) in post_details_page.current_url

    # Cleanup
    api.delete_post(phuongpv_api_client, created_post.id)
