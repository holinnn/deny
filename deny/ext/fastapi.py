import inspect
from functools import wraps
from typing import Any, Awaitable, Callable

from fastapi import Depends, Request

from deny import Ability, Permission

EndpointFunction = Callable[..., Awaitable[Any]]


def authorize_factory(ability_dependency: Callable[..., Ability]):
    """Factory to create the @authorize() decorator FastAPI.
    Since FastAPI relies on dependency injection we can use it to
    get the Ability object.
    But it would be annoying to pass the ability dependency all the time,
    to @authorize()
    (ex: @authorize(ProjectPermission.edit, ability: Ability = Depends(get_ability)))

    By using this factory we keep the ability dependency in cache.

    Example:

        def get_ability(request: Request):
            return Ability()
        authorize = authorize_factory(get_ability)

        @authorize(ProjectPermission.edit)
        async def edit_project(id: int):
            pass

        @authorize(ProjectPermission.view)
        async def view_project(id: int):
            pass

    Args:
        ability_dependency (Callable[..., Ability]): function returning
            the Ability object
    """

    def authorize(
        permission: Permission,
    ) -> Callable[[EndpointFunction], EndpointFunction]:
        def decorator(func: EndpointFunction) -> EndpointFunction:
            @wraps(func)
            async def wrapper(
                request: Request, ability: Ability, *args: Any, **kwargs: Any
            ) -> Any:
                await ability.authorize(permission, request=request, *args, **kwargs)
                return await func(*args, **kwargs)

            # we replace the wrapper signature in order to let FastAPI know that
            # it needs the `ability` and `request` dependency and
            # all the other parameters from the endpoint.
            wrapped_signature = inspect.signature(func)
            wrapper.__signature__ = inspect.Signature(  # type: ignore
                [
                    *list(wrapped_signature.parameters.values()),
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Request,
                    ),
                    inspect.Parameter(
                        "ability",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(ability_dependency),
                        annotation=Ability,
                    ),
                ]
            )
            return wrapper

        return decorator

    return authorize
