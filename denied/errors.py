from .permission import Permission


class UndefinedPermission(Exception):
    """Error raised when an Ability asks for a permission that is not
    set in the policy.
    """

    def __init__(self, permission: Permission) -> None:
        """
        Args:
            permission (Permission): a permission
        """
        super().__init__(f"Permission {permission.name} was not set in this policy")
        self.permission = permission


class UnauthorizedError(Exception):
    """Error raised by an Ability when the policy did not allow access
    for the permission.
    """

    def __init__(self, permission: Permission) -> None:
        """
        Args:
            permission (Permission): a permission
        """
        super().__init__(f"Access denied for permission {permission.name}")
        self.permission = permission


class PermissionAlreadyDefined(Exception):
    """Error raised while using the @authorize() decorator with the same Permission
    twice in the same Policy object.
    """

    def __init__(self, permission: Permission) -> None:
        """
        Args:
            permission (Permission): a permission
        """
        super().__init__(f"Permission {permission.name} already defined")
        self.permission = permission
