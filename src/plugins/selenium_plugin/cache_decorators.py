import os
from collections.abc import Callable
from functools import wraps
from typing import Any

import slugify
from _pytest.fixtures import FixtureRequest, SubRequest


def get_cache_name(request: SubRequest | FixtureRequest, name: str) -> str:
    """Return a string that represents location of cached fixture.

    A parameterized fixture may be appended with its __str__ representation.

    """
    return f"{slugify.slugify(os.environ['API_URL'])}/{request.getfixturevalue('worker_id')}/{name}"


def get_fixture_cache_name(request: SubRequest | FixtureRequest, fixture: Any) -> str:
    """Shortcut for generating cache name for fixture."""
    fixture_name = f"{fixture.__module__}.{fixture.__name__}"
    if isinstance(request, SubRequest) and hasattr(request, "param"):
        fixture_name += f".{request.param!s}"

    return get_cache_name(request=request, name=fixture_name)


def get_cache(
    request: SubRequest | FixtureRequest,
    func: Callable[..., Any] | None = None,
) -> Any | None:
    """Get cache of fixture."""
    if not request.config.getoption("--use-cache"):
        return None
    if isinstance(request, SubRequest):
        fixture = func if func else request._fixturedef.func  # cspell:disable-line
    elif isinstance(request, FixtureRequest):
        fixture = func if func else request.function
    fixture_name = get_fixture_cache_name(request=request, fixture=fixture)
    return request.config.cache.get(key=fixture_name, default=None)  # type: ignore


def fixture_cache(
    serializer: Callable[..., Any],
    deserializer: Callable[..., Any],
) -> Callable[..., Callable[..., Any]]:
    """Cache results of fixture to reuse it in next runs.

    Args:
        serializer: Function which is responsible for how to serialize result of fixture
            as dictionary(json module should be able to dump it).
        deserializer: Function which is responsible for how to deserialize cached data back

    """

    def _fixture_cache(fixture: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fixture)
        def wrapper(request: SubRequest, *args, **kwargs) -> Any:
            if not request.config.getoption("--use-cache"):
                return fixture(request, *args, **kwargs)
            cache_data = get_cache(request=request, func=fixture)
            if cache_data:
                return deserializer(cache_data=cache_data)
            result = fixture(request, *args, **kwargs)
            request.config.cache.set(  # type: ignore
                key=get_fixture_cache_name(request=request, fixture=fixture),
                value=serializer(api_object=result),
            )
            return result

        return wrapper

    return _fixture_cache
