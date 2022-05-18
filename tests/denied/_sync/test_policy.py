import pytest

from denied.errors import PermissionAlreadyDefined, UndefinedPermission
from denied.sync import Policy, authorize
from tests.utils.models import Project, User
from tests.utils.permissions import ProjectPermissions


class UserPolicy(Policy):
    def __init__(self, user: User) -> None:
        super().__init__()
        self._user = user

    @authorize(ProjectPermissions.edit)
    def can_edit_project(self, project: Project) -> bool:
        return project.owner_id == self._user.id


@pytest.fixture
def policy(user: User) -> UserPolicy:
    return UserPolicy(user)


@pytest.fixture
def user() -> User:
    return User(id=1)


class TestGetAccessMethod:
    def test_raise_exception_if_not_defined(self, policy: UserPolicy) -> None:
        with pytest.raises(UndefinedPermission):
            policy.get_access_method(ProjectPermissions.view)

    def test_return_access_method_if_defined(self, policy: UserPolicy) -> None:
        access_method = policy.get_access_method(ProjectPermissions.edit)
        assert access_method is not None
        assert access_method(Project(1)) is True


class TestMetaclass:
    def test_raise_error_if_permission_already_defined(self):
        with pytest.raises(PermissionAlreadyDefined):

            class _(Policy):
                @authorize(ProjectPermissions.edit)
                def can_edit_project(self) -> bool:
                    return False

                @authorize(ProjectPermissions.edit)
                def can_view_project(self) -> bool:
                    return False
