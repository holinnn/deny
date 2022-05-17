from typing import Any, Awaitable, Callable, Optional
from unittest.mock import ANY

import pytest
from pytest_mock import MockerFixture
from sanic import Sanic
from sanic.handlers import ErrorHandler as SanicErrorHandler
from sanic.request import Request
from sanic.response import HTTPResponse, json

from denied import Ability, Action, Policy
from denied import authorize as policy_authorize
from denied.errors import UnauthorizedError
from denied.ext.errors import AbilityNotFound
from denied.ext.sanic import authorize
from tests.utils.permissions import ProjectPermissions


@pytest.fixture
def endpoint() -> Callable[..., Awaitable[HTTPResponse]]:
    @authorize(ProjectPermissions.edit)
    async def get(request: Request, id: int) -> HTTPResponse:
        del request
        return json({"id": id})

    return get


class AbilityMiddleware:
    def __init__(self, ability: Ability) -> None:
        self._ability = ability

    async def __call__(self, request: Request) -> None:
        request.ctx.ability = self._ability


class ErrorHandler(SanicErrorHandler):
    error: Optional[Exception] = None

    def default(self, request: Request, exception: Exception):
        self.error = exception
        return super().default(request, exception)


class UserPolicy(Policy):
    @policy_authorize(ProjectPermissions.edit)
    async def can_edit_project(self, id: int, *args: Any, **kwargs: Any) -> bool:
        del id, args, kwargs
        return True


@pytest.fixture
def error_handler() -> ErrorHandler:
    return ErrorHandler()


@pytest.fixture
def app(error_handler: ErrorHandler, endpoint) -> Sanic:
    sanic_app = Sanic("test")
    sanic_app.error_handler = error_handler
    sanic_app.add_route(endpoint, "/<id:int>", methods=["GET"])
    return sanic_app


@pytest.fixture
def policy() -> UserPolicy:
    return UserPolicy()


class TestAuthorize:
    def test_raise_error_if_ability_is_not_found(
        self, app: Sanic, error_handler: ErrorHandler
    ) -> None:
        app.test_client.get("/1")
        assert isinstance(error_handler.error, AbilityNotFound)

    def test_execute_resource_if_authorized(self, app: Sanic) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.ALLOW)
        )
        app.middleware("request")(ability_middleware)
        _, response = app.test_client.get("/1")
        assert response.json == {"id": 1}

    def test_calls_policy_with_righ_arguments(
        self,
        app: Sanic,
        policy: UserPolicy,
        mocker: MockerFixture,
    ) -> None:
        can_edit_project = mocker.spy(policy, "can_edit_project")
        ability_middleware = AbilityMiddleware(ability=Ability(policy=policy))
        app.middleware("request")(ability_middleware)
        _, response = app.test_client.get("/1")
        assert response.json == {"id": 1}
        can_edit_project.assert_called_once_with(request=ANY, id=1)

    def test_raise_error_if_not_authorized(
        self, app: Sanic, error_handler: ErrorHandler
    ) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.DENY)
        )
        app.middleware("request")(ability_middleware)
        app.test_client.get("/1")
        assert isinstance(error_handler.error, UnauthorizedError)
