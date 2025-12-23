from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from pomcorn import locators

from pages.base_components import BlogComponent

if TYPE_CHECKING:
    from pages.base_pages import BlogPage


class BaseField(BlogComponent):
    """Base class for field components.

    `field_label` can be specified as component attribute or passed in `__init__` method.

    """

    page: BlogPage

    field_label: str = ""

    def __init__(
        self,
        page: BlogPage,
        field_label: str = "",
        base_locator: locators.XPathLocator = locators.XPathLocator(""),
        wait_until_visible: bool = True,
    ):
        self.field_label = field_label or self.field_label
        field_locator = base_locator // self.get_field_locator_by_label(self.field_label)

        super().__init__(
            page=page,
            base_locator=field_locator,
            wait_until_visible=wait_until_visible,
        )

    @property
    @abc.abstractmethod
    def value(self) -> Any:
        """Get current value of field."""

    @abc.abstractmethod
    def fill(self, value: Any) -> Any:
        """Fill field by value."""

    @staticmethod
    @abc.abstractmethod
    def get_field_locator_by_label(field_label: str) -> locators.XPathLocator:
        """Prepare field locator based on `field_label`."""

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear value of field."""
