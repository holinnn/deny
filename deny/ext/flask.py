from functools import wraps
from typing import Any, Callable, Optional

from flask import g, request

from deny.ext.errors import AbilityNotFound
from deny.sync import Ability, Permission

EndpointMethod = Callable[..., Any]


def authorize(permission: Permission, ability_key: str = "ability") -> EndpointMethod:
    """Flask's decorator for checking endpoints' permissions.
    The policy's access methods will be called with the request and
    all the other arguments and keyword arguments sent to the endpoint.

    Args:
        permission (Permission): a permission
        ability_key (str): key storing the ability object in the request.context
    """

    def decorator(func: EndpointMethod) -> EndpointMethod:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            ability: Optional[Ability] = g.get(ability_key)
            if ability:
                ability.authorize(permission, request=request, *args, **kwargs)
                return func(*args, **kwargs)
            else:
                raise AbilityNotFound(
                    f"Ability could not be found in g (ability_key={ability_key})"
                )

        return wrapper

    return decorator
