from http import HTTPStatus

from phuongpv_blog_api_client import AuthenticatedClient, models
from phuongpv_blog_api_client.api.posts import posts_destroy, posts_list, posts_retrieve
from phuongpv_blog_api_client.types import Unset

from .decorators import is_exists


def get_post_by_name(client: AuthenticatedClient, post_name: str) -> models.Post | None:
    """Retrieve a blog post by its name."""
    post_response = posts_list.sync(
        client=client,
        search=post_name,
    )
    assert isinstance(post_response, models.PaginatedPostList), post_response
    assert len(post_response.results) == 1
    return post_response.results[0]


is_post_exists = is_exists(get_post_by_name)


def get_post_by_id(client: AuthenticatedClient, post_id: int) -> models.Post | None:
    """Retrieve a blog post by its ID."""
    post_response = posts_retrieve.sync(
        client=client,
        id=post_id,
    )
    assert isinstance(post_response, models.Post), post_response
    return post_response


def delete_post(client: AuthenticatedClient, post_id: int | Unset) -> None:
    """Delete a blog post by its ID."""
    assert post_id
    delete_response = posts_destroy.sync_detailed(client=client, id=post_id)
    assert delete_response.status_code == HTTPStatus.NO_CONTENT, delete_response
