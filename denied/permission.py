from typing import Any


class Permission:
    def __init__(self, name: str) -> None:
        """
        Args:
            name (str): permission name
        """
        self.name = name


class AutoPermission:
    """Descriptor used to create Permission objects
    with automatic name generation.
    """

    def __init__(self) -> None:
        self._permission = Permission(name="")

    def __set_name__(self, owner: Any, name: str) -> None:
        self._permission.name = f"{owner.__name__}.{name}"

    def __get__(self, *_: Any) -> Permission:
        return self._permission
