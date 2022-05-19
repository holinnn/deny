from functools import wraps
from typing import Any, Awaitable, Callable, Optional

from falcon import Request
from falcon.response import Response

from deny import Ability
from deny.ext.errors import AbilityNotFound
from deny.permission import Permission

ResourceMethod = Callable[..., Awaitable[None]]


def authorize(
    permission: Permission, ability_key: str = "ability"
) -> Callable[[ResourceMethod], ResourceMethod]:
    """Falcon's decorator for checking endpoints' permissions.
    The policy's access methods will be called with the request and
    all the other arguments and keyword arguments sent to the endpoint.

    Args:
        permission (Permission): a permission
        ability_key (str): key storing the ability object in the request.context
    """

    def decorator(func: ResourceMethod) -> ResourceMethod:
        @wraps(func)
        async def wrapper(
            resource: Any, req: Request, resp: Response, *args: Any, **kwargs: Any
        ) -> None:
            ability: Optional[Ability] = req.context.get(ability_key)
            if ability:
                await ability.authorize(permission, request=req, *args, **kwargs)
                await func(resource, req, resp, *args, **kwargs)
            else:
                raise AbilityNotFound(
                    "Ability could not be found in "
                    f"request.context (ability_key={ability_key})"
                )

        return wrapper

    return decorator
