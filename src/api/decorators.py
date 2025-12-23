from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

APIObject = TypeVar("APIObject")
FunctionParams = ParamSpec("FunctionParams")
AttrValue = TypeVar("AttrValue")


def is_exists(
    api_function: Callable[FunctionParams, APIObject],
) -> Callable[FunctionParams, bool]:
    """Decorate `get_{model}_by_something` functions of `api` module.

    Allows to create simple shortcuts for `is_{model}_exists` methods to check that the model
    created in the test was also created in the api.

    Return boolean indicating if `{APIObject}` exists.

    Example:
        def get_post_by_name(
            client: AuthenticatedClient,
            post_name: str,
        ) -> models.Post:
            ...

        is_post_exists = is_exists(get_post_by_name)

    """

    @wraps(api_function)
    def wrapper(
        *args: FunctionParams.args,
        **kwargs: FunctionParams.kwargs,
    ) -> bool:
        try:
            api_function(*args, **kwargs)
        except AssertionError:
            return False
        return True

    return wrapper
