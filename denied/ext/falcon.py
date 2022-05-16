from typing import Any, Callable, Optional

from falcon import Request
from falcon.response import Response

from denied.ability import Ability
from denied.ext.errors import AbilityNotFound
from denied.permission import Permission

ResourceMethod = Callable[[Any, Request, Any, Any], None]


def authorize(permission: Permission, ability_key: str = "ability"):
    """Falcon's decorator for checking endpoints' permissions.
    The policy's access methods will be called with the request and
    all the other arguments and keyword arguments sent to the endpoint.

    Args:
        permission (Permission): a permission
        ability_key (str): key storing the ability object in the request.context
    """

    def decorator(func: ResourceMethod) -> ResourceMethod:
        def wrapper(
            resource: Any, req: Request, resp: Response, *args: Any, **kwargs: Any
        ) -> None:
            ability: Optional[Ability] = req.context.get(ability_key)
            if ability:
                ability.authorize(permission, request=req, *args, **kwargs)
                func(resource, req, resp, *args, **kwargs)
            else:
                raise AbilityNotFound(
                    "Ability could not be found in "
                    f"request.context (ability_key={ability_key})"
                )

        return wrapper

    return decorator
