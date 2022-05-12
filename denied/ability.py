from enum import Enum
from typing import Any, Optional

from denied.errors import UnauthorizedError, UndefinedPermission
from denied.permission import Permission
from denied.policy import Policy


class Action(Enum):
    DENY = "deny"
    ALLOW = "allow"
    RAISE = "raise"


class Ability:
    def __init__(
        self, policy: Optional[Policy] = None, default_action: Action = Action.DENY
    ):
        self._policy = policy or Policy()
        self._default_action = default_action

    def authorize(self, permission: Permission, *args, **kwargs) -> None:
        if not self.can(permission, *args, **kwargs):
            raise UnauthorizedError(permission)

    def can(self, permission: Permission, *args: Any, **kwargs: Any) -> bool:
        try:
            access_method = self._policy.get_access_method(permission)
        except UndefinedPermission as error:
            if self._default_action == Action.RAISE:
                raise error
            else:
                return True if self._default_action == Action.ALLOW else False

        return access_method(*args, **kwargs)
