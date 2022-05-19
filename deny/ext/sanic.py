from functools import wraps
from typing import Any, Callable, Optional

from sanic.models.handler_types import RouteHandler
from sanic.request import Request
from sanic.response import HTTPResponse

from deny import Ability, Permission
from deny.ext.errors import AbilityNotFound


def authorize(
    permission: Permission, ability_key: str = "ability"
) -> Callable[[RouteHandler], RouteHandler]:
    """Sanic's decorator for checking endpoints' permissions.
    The policy's access methods will be called with the request and
    all the other arguments and keyword arguments sent to the endpoint.

    Args:
        permission (Permission): a permission
        ability_key (str): key storing the ability object in the request.ctx
    """

    def decorator(func: RouteHandler) -> RouteHandler:
        @wraps(func)
        async def wrapper(
            request: Request, *args: Any, **kwargs: Any
        ) -> Optional[HTTPResponse]:
            ability: Optional[Ability] = getattr(request.ctx, ability_key, None)
            if ability:
                await ability.authorize(permission, request=request, *args, **kwargs)
                return await func(request, *args, **kwargs)
            else:
                raise AbilityNotFound(
                    "Ability could not be found in "
                    f"request.ctx (ability_key={ability_key})"
                )

        return wrapper

    return decorator
