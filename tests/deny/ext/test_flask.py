from typing import Any, Callable, Optional, Tuple
from unittest.mock import ANY

import pytest
from flask import Flask, g, jsonify
from flask.testing import FlaskClient
from flask.wrappers import Response
from pytest_mock import MockerFixture

from deny.errors import UnauthorizedError
from deny.ext.errors import AbilityNotFound
from deny.ext.flask import authorize
from deny.sync import Ability, Action, Policy
from deny.sync import authorize as policy_authorize
from tests.utils.permissions import ProjectPermissions


class ErrorHandler:
    error: Optional[Exception] = None

    def __call__(self, error: Exception) -> Tuple[str, int]:
        self.error = error
        return "", 500


class UserPolicy(Policy):
    @policy_authorize(ProjectPermissions.edit)
    def can_edit_project(self, id: int, *args: Any, **kwargs: Any) -> bool:
        del id, args, kwargs
        return True


class AbilityMiddleware:
    def __init__(self, ability: Ability) -> None:
        self._ability = ability

    def __call__(self) -> None:
        g.ability = self._ability


@pytest.fixture
def error_handler() -> ErrorHandler:
    return ErrorHandler()


@pytest.fixture
def endpoint() -> Callable[..., str]:
    @authorize(ProjectPermissions.edit)
    def edit_project(id: int) -> Response:
        return jsonify({"id": id})

    return edit_project


@pytest.fixture
def app(error_handler: ErrorHandler, endpoint: Callable[..., str]) -> Flask:
    flask_app = Flask("tests")
    flask_app.errorhandler(Exception)(error_handler)
    flask_app.route("/<int:id>")(endpoint)
    return flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def policy() -> UserPolicy:
    return UserPolicy()


class TestAuthorize:
    def test_raise_error_if_ability_is_not_found(
        self, client: FlaskClient, error_handler
    ) -> None:
        client.get("/1")
        assert isinstance(error_handler.error, AbilityNotFound)

    def test_execute_resource_if_authorized(
        self,
        client: FlaskClient,
        app: Flask,
    ) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.ALLOW)
        )
        app.before_request(ability_middleware)
        response = client.get("/1")
        assert response.json == {"id": 1}

    def test_calls_policy_with_righ_arguments(
        self,
        client: FlaskClient,
        app: Flask,
        policy: UserPolicy,
        mocker: MockerFixture,
    ) -> None:
        can_edit_project = mocker.spy(policy, "can_edit_project")
        ability_middleware = AbilityMiddleware(ability=Ability(policy=policy))
        app.before_request(ability_middleware)
        response = client.get("/1")
        assert response.json == {"id": 1}
        can_edit_project.assert_called_once_with(request=ANY, id=1)

    def test_raise_error_if_not_authorized(
        self, client: FlaskClient, app: Flask, error_handler: ErrorHandler
    ) -> None:
        ability_middleware = AbilityMiddleware(
            ability=Ability(default_action=Action.DENY)
        )
        app.before_request(ability_middleware)
        client.get("/1")
        assert isinstance(error_handler.error, UnauthorizedError)
