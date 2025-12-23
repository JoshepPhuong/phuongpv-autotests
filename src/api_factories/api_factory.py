import typing
from collections.abc import Callable, Generator
from contextlib import suppress
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from _pytest.fixtures import SubRequest

from plugins.selenium_plugin.cache_decorators import get_cache

APIObject = TypeVar("APIObject")
FactoryParams = ParamSpec("FactoryParams")
AttrValue = TypeVar("AttrValue")
FactoryGenerator: typing.TypeAlias = Generator[APIObject]


def api_factory(
    factory: Callable[FactoryParams, FactoryGenerator[APIObject]],
) -> Callable[Concatenate[SubRequest, FactoryParams], APIObject]:
    """Prepare API factory from generator functions.

    This decorator adds finalizer to pytest.SubRequest that allows run
    instructions after `yield` statement, for example, remove created object
    via API.

    API factory function should return generator object that yield a single
    object, e.g.:

    ```
    @api_factory
    def example_factory(*args) -> FactoryGenerator[ExampleObject]:
        # create object via API
        created_object = cms_api.ExampleApi().create_object(
            ExampleObject(*args),
        )
        yield created_object
        # remove object via API
        cms_api.ExampleApi().delete_object(created_object.id)

    ```

    Decorated function requires `request` argument and will be finished after
    the last test within the requesting test context finished execution.

    There was an attempt to implement the `delete_from_api` logic that we write in each factory
    directly in the decorator.
    But this approach looks impossible,
    because `Concatenate` cannot accept optional or keyword arguments.
    https://peps.python.org/pep-0612/#concatenating-keyword-parameters

    """

    @wraps(factory)
    def wrapper(
        request: SubRequest,
        *args: FactoryParams.args,
        **kwargs: FactoryParams.kwargs,
    ) -> APIObject:
        factory_generator = factory(*args, **kwargs)

        def _finalize_generator(generator: FactoryGenerator[APIObject]) -> None:
            """Suppress exception to allow running code after `yield`.

            Function-based factory is generator object with just one yielded
            object that should have the following structure:

                Init object -> yield object -> remove object

            To make possible to run the code after `yield` just suppress
            `StopIteration` exception and call `next`.

            """
            # When caching enabled do not delete objects from API
            if get_cache(request):
                return
            with suppress(StopIteration):
                next(generator)

        request.addfinalizer(lambda: _finalize_generator(factory_generator))

        return next(factory_generator)

    return wrapper


class _Default:
    """Singleton to use as default value for API factories.

    We have to set default values for most of the API factory arguments,
    but some fields can be nullable in some cases (i.e. `None` is
    valid value), but shouldn't be `None` by default. For these cases just use
    `Default` singleton value, for example:

        @api_factory
        def example_factory(
            example_attribute: int = Default,
        ):
            if example_attribute is Default:
                example_attribute = 1

            yield ExampleObject(
                example_attribute=example_attribute,
            )

    """

    def __bool__(self) -> typing.Literal[False]:
        """Allow `Default` to be used like `None`/`False` in bool expressions."""
        return False


Default: typing.Any = _Default()
