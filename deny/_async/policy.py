import inspect
from typing import Any, Callable, Dict, List, Tuple

from deny.errors import PermissionAlreadyDefined, UndefinedPermission
from deny.permission import Permission
from deny.utils import AccessMethod

_AUTHORIZED_PERMISSIONS_ATTR = "_authorized_permissions"


class PolicyMetaclass(type):
    """Metaclass used by the Policy class.
    It's used to register all the access methods defined by the @authorize() decorator.
    """

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]) -> type:
        """Callback called when a Policy class is created.
        Loop over all the attributes and check if a `_authorized_permission` has
        been defined on it.
        If `_authorized_permission` is found we register the method
        in a dictionary in order to access it later using the
        permission being authorized.

        Args:
            cls: a Policy class
            name (str): class name
            bases (Tuple[type, ...]): base classes
            attrs (Dict[str, Any]): class attributes
        """
        # add the methods from base classes to the ones that will be checked
        attributes_to_check = attrs.copy()
        for base in bases:
            base_methods = inspect.getmembers(base, predicate=inspect.isfunction)
            for base_method in base_methods:
                attributes_to_check[base_method[0]] = base_method[1]

        # check if @autorize() was used for each method and register
        # the ones that grant a permission
        access_methods: Dict[Permission, str] = {}
        for name, value in attributes_to_check.items():
            permissions: List[Permission] = getattr(
                value, _AUTHORIZED_PERMISSIONS_ATTR, []
            )

            for permission in permissions:
                if permission in access_methods:
                    raise PermissionAlreadyDefined(permission)
                access_methods[permission] = name

        attrs["_access_methods"] = access_methods
        return super().__new__(cls, name, bases, attrs)


def authorize(permission: Permission) -> Callable[[AccessMethod], AccessMethod]:
    def decorator(func: AccessMethod) -> AccessMethod:
        """Add an `_authorized_permission` attribute to the method
        in order for the metaclass to recognize it as an AccessMethod.

        Args:
            func (AccessMethod): method used to grant access

        Returns:
            AccessMethod: access method received as input
        """
        if hasattr(func, _AUTHORIZED_PERMISSIONS_ATTR):
            permissions = getattr(func, _AUTHORIZED_PERMISSIONS_ATTR)
        else:
            permissions = []
            setattr(func, _AUTHORIZED_PERMISSIONS_ATTR, permissions)

        permissions.append(permission)
        return func

    return decorator


class Policy(metaclass=PolicyMetaclass):
    _access_methods: Dict[Permission, str]

    def get_access_method(self, permission: Permission) -> AccessMethod:
        """Returns the AccessMethod that was registered for the permission
        received as input.
        If no AccessMethod is found it raises a UndefinedPermission error.

        Args:
            permission (Permission): a permission

        Returns:
            AccessMethod: access method registered for permission
        """
        try:
            return getattr(self, self._access_methods[permission])
        except KeyError:
            raise UndefinedPermission(permission)
