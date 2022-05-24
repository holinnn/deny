from typing import Any

from deny import AutoPermission, Permission, Policy, authorize
from deny.sync import Policy as SyncPolicy
from deny.sync import authorize as sync_authorize


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


class SyncUserPolicy(SyncPolicy):
    @sync_authorize(ProjectPermissions.edit)
    @sync_authorize(ProjectPermissions.view)
    def can_edit_project(self, request: Any, id: int) -> bool:
        return id == 1
