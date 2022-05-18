from types import SimpleNamespace
from typing import Awaitable, Callable, Dict
from unittest.mock import ANY

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from denied import Ability, Policy
from denied import authorize as policy_authorize
from denied.errors import UnauthorizedError
from denied.ext.fastapi import authorize_factory
from tests.utils.permissions import ProjectPermissions


class UserPolicy(Policy):
    @policy_authorize(ProjectPermissions.edit)
    async def can_edit_project(self, id: int, request: Request) -> bool:
        del request
        return id == 1


@pytest.fixture
def ability(policy: UserPolicy) -> Ability:
    return Ability(policy=policy)


@pytest.fixture
def endpoint() -> Callable[[int], Awaitable[Dict[str, int]]]:
    async def get(id: int) -> Dict[str, int]:
        return {"id": id}

    return get


@pytest.fixture
def error_recorder() -> SimpleNamespace:
    return SimpleNamespace()


@pytest.fixture
def app(error_recorder: SimpleNamespace, ability: Ability, endpoint) -> FastAPI:
    authorize = authorize_factory(lambda: ability)
    fastapi_app = FastAPI()

    @fastapi_app.exception_handler(UnauthorizedError)
    async def _(request: Request, exc: Exception):
        del request
        error_recorder.error = exc
        return Response(status_code=500)

    authorized_endpoint = authorize(ProjectPermissions.edit)(endpoint)
    fastapi_app.get("/{id}")(authorized_endpoint)
    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def policy() -> UserPolicy:
    return UserPolicy()


class TestAuthorize:
    def test_execute_resource_if_authorized(self, client: TestClient) -> None:
        response = client.get("/1")
        assert response.json() == {"id": 1}

    def test_calls_policy_with_righ_arguments(
        self,
        client: TestClient,
        policy: UserPolicy,
        mocker: MockerFixture,
    ) -> None:
        can_edit_project = mocker.spy(policy, "can_edit_project")
        response = client.get("/1")
        assert response.json() == {"id": 1}
        can_edit_project.assert_called_once_with(id=1, request=ANY)

    def test_raise_error_if_not_authorized(
        self, client: TestClient, error_recorder: SimpleNamespace
    ) -> None:
        client.get("/2")
        assert isinstance(error_recorder.error, UnauthorizedError)
