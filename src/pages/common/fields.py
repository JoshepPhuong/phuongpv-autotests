from typing import Generic, NoReturn, TypeAlias, TypeVar, get_args

from pomcorn import Component, Page, locators

from . import fields_components
from .base_field import BaseField

TField = TypeVar("TField", bound=BaseField)

Instance: TypeAlias = Component | Page  # type: ignore[type-arg]


class BaseFormDescriptor(Generic[TField]):
    """Descriptor for easier way to init attributes in form components.

    Get field class from `Generic` param and return a cached instance
        each time this attribute is called.

    """

    cache_attribute_name = "cached_elements"

    def __init__(self, field_label: str | None = None) -> None:
        self.field_label = field_label

    @property
    def component(self) -> type:
        """Return class passed in `Generic[TField]`."""
        return get_args(self.__orig_bases__[0])[0]  # type: ignore

    def __set_name__(self, _owner: Instance, name: str) -> None:  # type: ignore[type-arg]
        """Save attribute name for which descriptor is created."""
        self.attribute_name = name

    def __get__(
        self,
        instance: Instance | None,  # type: ignore[type-arg]
        _type: type[Instance],  # type: ignore[type-arg]
    ) -> TField:
        """Get field component by stored `field_label`."""
        if not instance:
            raise ValueError(
                "Use of this descriptor is only available inside `BaseForm` based components.",
            )
        return self.prepare_component(instance)

    def prepare_component(self, instance: Instance) -> TField:  # type: ignore[type-arg]
        """Init component and cache it.

        Initiate component only once, and then store it in an instance and return it each
            subsequent time. This is to avoid calling `wait_until_visible` multiple times
            in the init of component.

        If the instance doesn't already have an attribute to store cache, it will be set.

        """
        if not getattr(instance, self.cache_attribute_name, None):
            setattr(instance, self.cache_attribute_name, {})

        cache: dict[str, TField] = getattr(instance, self.cache_attribute_name)
        if cached_component := cache.get(self.attribute_name):
            return cached_component

        if isinstance(instance, Page):
            page = instance
            base_locator = locators.XPathLocator("")
        else:  # if isinstance is `Component`
            page = instance.page
            base_locator = instance.base_locator

        component: TField = self.component(
            page=page,
            field_label=self.field_label,
            base_locator=base_locator,
        )
        cache[self.attribute_name] = component

        return component

    def __set__(self, *args, **kwargs) -> NoReturn:
        raise ValueError("You can't reset an form component attribute value!")


class Input(BaseFormDescriptor[fields_components.InputComponent]):
    """Descriptor for easier way to init input attributes in form components."""


class TextArea(BaseFormDescriptor[fields_components.TextAreaComponent]):
    """Descriptor for easier way to init textarea attributes in form components."""
