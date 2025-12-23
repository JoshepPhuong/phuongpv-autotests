import functools
import re
from types import ModuleType
from typing import Any, Protocol, TypeAlias, TypedDict, TypeVar, cast

import phuongpv_blog_api_client.models

from plugins.selenium_plugin.cache_decorators import fixture_cache

T = TypeVar("T", bound="OpenApiModel")


class OpenApiModel(Protocol):
    """Represent interface of generated API objects from SDK."""

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T: ...


CacheDataDict: TypeAlias = dict[str, Any] | list[dict[str, Any]] | tuple[dict[str, Any], ...]


class CacheData(TypedDict):
    """Represent structure of cached data."""

    response_type: str
    data: CacheDataDict


def _openapi_serializer(
    api_object: OpenApiModel | list[OpenApiModel],
) -> CacheData:
    """Serialize response object to store in cache."""
    response_data: CacheDataDict
    if isinstance(api_object, list):
        response_type = f"list[{api_object[0].__class__.__name__}]"
        response_data = [api_item.to_dict() for api_item in api_object]
    elif isinstance(api_object, tuple):
        response_type = f"tuple[{api_object[0].__class__.__name__}, ...]"
        response_data = tuple(api_item.to_dict() for api_item in api_object)

    else:
        response_type = api_object.__class__.__name__
        response_data = api_object.to_dict()

    return {
        "response_type": response_type,
        "data": response_data,
    }


def _openapi_deserializer(
    models_module: ModuleType,
    cache_data: CacheData,
) -> list[OpenApiModel] | tuple[OpenApiModel, ...] | OpenApiModel:
    """Deserialize openapi object from cache."""
    response_type = cache_data["response_type"]
    response_data = cache_data["data"]

    object_model_class: OpenApiModel

    if response_type.startswith("list["):
        response_type_match = re.match(r"list\[(.*)\]", response_type)
        if response_type_match is None:
            raise ValueError(f"Unknown response type: {response_type}")
        object_model = response_type_match.group(1)
        object_model_class = getattr(models_module, object_model)

        response_data = cast(list[dict[str, Any]], response_data)
        return [object_model_class.from_dict(sub_data) for sub_data in response_data]

    elif response_type.startswith("tuple["):
        response_type_match = re.match(r"tuple\[(.*), \.\.\.\]", response_type)
        if response_type_match is None:
            raise ValueError(f"Unknown response type: {response_type}")
        object_model = response_type_match.group(1)
        object_model_class = getattr(models_module, object_model)

        response_data = cast(tuple[dict[str, Any], ...], response_data)
        return tuple(object_model_class.from_dict(sub_data) for sub_data in response_data)

    response_data = cast(dict[str, Any], response_data)
    object_model_class = getattr(models_module, response_type)
    return object_model_class.from_dict(response_data)


cms_openapi_fixture_cache = fixture_cache(
    serializer=_openapi_serializer,
    deserializer=functools.partial(
        _openapi_deserializer,
        models_module=phuongpv_blog_api_client.models,
    ),
)
