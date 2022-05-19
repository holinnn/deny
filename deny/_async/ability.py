from typing import Any, Optional

from deny.action import Action
from deny.errors import UnauthorizedError, UndefinedPermission
from deny.permission import Permission

from .policy import Policy


class Ability:
    def __init__(
        self, policy: Optional[Policy] = None, default_action: Action = Action.DENY
    ):
        """
        Args:
            policy (Optional[Policy]): policy that will be checked for permissions
            default_action (Action): action used when the permission
                was not set on policy
        """
        self._policy = policy or Policy()
        self._default_action = default_action

    async def authorize(
        self, permission: Permission, *args: Any, **kwargs: Any
    ) -> None:
        """Raises an UnauthorizedError if policy does not grant permission.

        Args:
            permission (Permission): a permission
            args (Any): arguments passed to the policy access method
            kwargs (Any): keyword argumentss passed to the policy access method

        Returns:
            None:
        """
        if not await self.can(permission, *args, **kwargs):
            raise UnauthorizedError(permission)

    async def can(self, permission: Permission, *args: Any, **kwargs: Any) -> bool:
        """Returns the result of the policy access method defined for the permission.
        If no access method is found the default_action is used.
        If permission was not defined and default_action is RAISE then an
        UndefinedPermission is raised.

        Args:
            permission (Permission): a permission
            args (Any): arguments passed to the policy access method
            kwargs (Any): keyword argumentss passed to the policy access method

        Returns:
            bool: True if permission is granted, False otherwise
        """
        try:
            access_method = self._policy.get_access_method(permission)
        except UndefinedPermission as error:
            if self._default_action == Action.RAISE:
                raise error
            else:
                return True if self._default_action == Action.ALLOW else False

        return await access_method(*args, **kwargs)
