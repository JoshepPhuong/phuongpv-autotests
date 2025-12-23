from pomcorn import locators

from ..base_field import BaseField


class InputComponent(BaseField):
    """Represent base input element in form."""

    @property
    def is_enabled(self) -> bool:
        return self.body.is_enabled

    @property
    def value(self) -> str:
        return self.body.get_value()

    def clear(self, only_visible: bool = True) -> None:
        return self.body.clear(only_visible=only_visible)

    def fill(
        self,
        text: str | int | float,
        only_visible: bool = True,
        clear: bool = True,
    ) -> None:
        return self.body.fill(str(text), only_visible, clear)

    def get_field_locator_by_label(self, field_label: str) -> locators.XPathLocator:
        """Prepare input locator based on `field_label`."""
        return locators.XPathLocator(f"//*[contains(., '{field_label}')]/following::input[1]")


class TextAreaComponent(InputComponent):
    """Represent a textarea element in form."""

    def get_field_locator_by_label(self, field_label: str) -> locators.XPathLocator:
        """Prepare input locator based on `field_label`."""
        return locators.XPathLocator(
            f"//*[contains(., '{field_label}')]/following::textarea[1]",
        )
