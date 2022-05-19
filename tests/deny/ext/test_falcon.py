import json
from typing import Any, Dict, Optional
from unittest.mock import ANY

import pytest
from falcon import Request, Response, testing
from falcon.asgi import App
from pytest_mock import MockerFixture

from deny import Ability, Action, Policy
from deny import authorize as policy_authorize
from deny.errors import UnauthorizedError
from deny.ext.errors import AbilityNotFound
from deny.ext.falcon import authorize
from tests.utils.permissions import ProjectPermissions


class Resource:
    @authorize(ProjectPermissions.edit)
    async def on_get(self, _: Request, resp: Response, id: int) -> None:
        resp.text = json.dumps({"id": id})


class AbilityMiddleware:
    def __init__(self, ability: Ability) -> None:
        self._ability = ability

    async def process_request(self, req: Request, _: Response) -> None:
        req.context["ability"] = self._ability


class ErrorHandler:
    error: Optional[Exception] = None

    async def __call__(
        self, req: Request, resp: Response, error: Exception, params: Dict[str, Any]
    ) -> None:
        del req, resp, params
        self.error = error


class UserPolicy(Policy):
    @policy_authorize(ProjectPermissions.edit)
    async def can_edit_project(self, id: int, *args: Any, **kwargs: Any) -> bool:
        del id, args, kwargs
        return True


@pytest.fixture
def error_handler() -> ErrorHandler:
    return ErrorHandler()


@pytest.fixture
def app(error_handler: ErrorHandler) -> App:
    falcon_app = App()
    falcon_app.add_error_handler(Exception, error_handler)
    falcon_app.add_route("/{id:int}", Resource())
    return falcon_app


@pytest.fixture
def client(app: App) -> testing.TestClient:
    return testing.TestClient(app)


@pytest.fixture
def policy() -> UserPolicy:
    return UserPolicy()


class TestAuthorize:
    def test_raise_error_if_ability_is_not_found(
        self, client: testing.TestClient, error_handler
    ) -> None:
        client.simulate_get("/1")
        assert isinstance(error_handler.error, AbilityNotFound)

    def test_execute_resource_if_authorized(
        self, client: testing.TestClient, app: App
    ) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.ALLOW)
        )
        app.add_middleware(ability_middleware)
        response = client.simulate_get("/1")
        assert response.json == {"id": 1}

    def test_calls_policy_with_righ_arguments(
        self,
        client: testing.TestClient,
        app: App,
        policy: UserPolicy,
        mocker: MockerFixture,
    ) -> None:
        can_edit_project = mocker.spy(policy, "can_edit_project")
        ability_middleware = AbilityMiddleware(ability=Ability(policy=policy))
        app.add_middleware(ability_middleware)
        response = client.simulate_get("/1")
        assert response.json == {"id": 1}
        can_edit_project.assert_called_once_with(request=ANY, id=1)

    def test_raise_error_if_not_authorized(
        self, client: testing.TestClient, app: App, error_handler: ErrorHandler
    ) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.DENY)
        )
        app.add_middleware(ability_middleware)
        client.simulate_get("/1")
        assert isinstance(error_handler.error, UnauthorizedError)
