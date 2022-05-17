from denied import AutoPermission, Permission


class ProjectPermissions:
    edit = AutoPermission()


class TestSetName:
    def test_set_name_of_the_permission(self):
        assert ProjectPermissions.edit.name == "ProjectPermissions.edit"


class TestGet:
    def test_returns_permission_instance(self):
        assert isinstance(ProjectPermissions.edit, Permission)
