from typing import TYPE_CHECKING

from pomcorn import Component

if TYPE_CHECKING:
    from pages.base_pages import BlogPage


class BlogComponent(Component["BlogPage"]):
    """Represent component of PhuongPV Blog.

    Jetbrains has some issues with type checking and autocompletion when using generic
    parametrization.

    So to avoid this issue, lets use a new class instead of TypeAlias.

    Issues:
        https://youtrack.jetbrains.com/issue/PY-61489
        https://youtrack.jetbrains.com/issue/PY-57731

    """
