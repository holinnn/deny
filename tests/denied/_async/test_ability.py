import pytest

from denied import Ability, Action, Policy, authorize
from denied.errors import UnauthorizedError, UndefinedPermission
from tests.utils.models import Project, User
from tests.utils.permissions import ProjectPermissions


class UserPolicy(Policy):
    def __init__(self, user: User) -> None:
        self._user = user

    @authorize(ProjectPermissions.view)
    async def can_view_project(self, project: Project):
        return self._user.id == project.owner_id


@pytest.fixture
def user() -> User:
    return User(id=1)


@pytest.fixture
def policy(user: User) -> UserPolicy:
    return UserPolicy(user=user)


@pytest.fixture
def ability(policy: UserPolicy) -> Ability:
    return Ability(policy=policy)


@pytest.fixture
def authorized_project(user: User) -> Project:
    return Project(owner_id=user.id)


@pytest.fixture
def unauthorized_project() -> Project:
    return Project(owner_id=2)


class TestAuthorize:
    async def test_returns_does_not_raise_error_if_authorized(
        self, ability: Ability, authorized_project: Project
    ) -> None:
        await ability.authorize(ProjectPermissions.view, authorized_project)

    async def test_returns_raise_error_if_not_authorized(
        self, ability: Ability, unauthorized_project: Project
    ) -> None:
        with pytest.raises(UnauthorizedError):
            await ability.authorize(ProjectPermissions.view, unauthorized_project)


class TestCan:
    async def test_returns_true_if_authorized(
        self, ability: Ability, authorized_project: Project
    ) -> None:
        assert await ability.can(ProjectPermissions.view, authorized_project) is True

    async def test_returns_false_if_not_authorized(
        self, ability: Ability, unauthorized_project: Project
    ) -> None:
        assert await ability.can(ProjectPermissions.view, unauthorized_project) is False

    async def test_raise_error_if_permission_not_defined_and_default_action_is_raise(
        self,
    ) -> None:
        ability = Ability(default_action=Action.RAISE)
        with pytest.raises(UndefinedPermission):
            await ability.can(ProjectPermissions.edit)

    async def test_returns_true_of_permission_not_defined_and_default_action_is_allow(
        self,
    ):
        ability = Ability(default_action=Action.ALLOW)
        assert await ability.can(ProjectPermissions.edit) is True

    async def test_returns_false_of_permission_not_defined_and_default_action_is_deny(
        self,
    ):
        ability = Ability(default_action=Action.DENY)
        assert await ability.can(ProjectPermissions.edit) is False
