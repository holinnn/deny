from typing import Optional

from denied.errors import UnauthorizedError
from denied.sync import Ability, AutoPermission, Permission, Policy, authorize


class ProfilePermissions:
    view = Permission(name="view_project")
    edit = (
        AutoPermission()
    )  # name will be automatically set to "ProjectPermissions.edit"


class SessionPermissions:
    create = AutoPermission()
    delete = AutoPermission()


class LoggedInUser:
    @authorize(SessionPermissions.delete)
    def can_logout(self):
        return True


class AnonymousUserPolicy(Policy):
    @authorize(SessionPermissions.create)
    def can_logout(self):
        return True


class UserPolicy(LoggedInUser, Policy):
    def __init__(self, current_user_id: int):
        self._current_user_id = current_user_id

    @authorize(ProfilePermissions.edit)
    def can_edit_profile(self, user_id: int) -> bool:
        """Only current user can edit his own profile."""
        return self._current_user_id == user_id

    @authorize(ProfilePermissions.view)
    def can_view_profile(self, user_id: int) -> bool:
        """Everybody can view the user profiles."""
        return True


def get_ability(current_user_id: Optional[int]) -> Ability:
    policy: Optional[Policy] = None
    if current_user_id:
        policy = UserPolicy(current_user_id)
    else:
        policy = AnonymousUserPolicy()

    return Ability(policy=policy)


################
# Logged in user
ability = get_ability(1)
assert ability.can(ProfilePermissions.view, 1) is True
assert ability.can(ProfilePermissions.view, 2) is True
assert ability.can(ProfilePermissions.edit, 1) is True
ability.authorize(ProfilePermissions.edit, 1)  # does not throw any error
assert ability.can(ProfilePermissions.edit, 2) is False
try:
    ability.authorize(ProfilePermissions.edit, 2)  # throw an UnauthorizedError
except UnauthorizedError:
    pass
assert ability.can(SessionPermissions.create) is False
assert ability.can(SessionPermissions.delete) is True

################
# Anonymous user
ability = get_ability(None)
assert ability.can(ProfilePermissions.view, 1) is False
assert ability.can(ProfilePermissions.view, 2) is False
assert ability.can(ProfilePermissions.edit, 1) is False
try:
    ability.authorize(ProfilePermissions.edit, 1)  # throw an UnauthorizedError
except UnauthorizedError:
    pass
assert ability.can(ProfilePermissions.edit, 2) is False
try:
    ability.authorize(ProfilePermissions.edit, 2)  # throw an UnauthorizedError
except UnauthorizedError:
    pass
assert ability.can(SessionPermissions.create) is True
assert ability.can(SessionPermissions.delete) is False
