from typing import Any

from denied import AutoPermission, Permission, Policy, authorize


class ProjectPermissions:
    view = Permission(name="view_project")
    edit = (
        AutoPermission()
    )  # name will be automatically set to "ProjectPermissions.edit"


class UserPolicy(Policy):
    @authorize(ProjectPermissions.edit)
    @authorize(ProjectPermissions.view)
    async def can_edit_project(self, request: Any, id: int) -> bool:
        return id == 1
