from deny.permission import AutoPermission


class ProjectPermissions:
    view = AutoPermission()
    edit = AutoPermission()
    delete = AutoPermission()


class SessionPermissions:
    delete = AutoPermission()
    create = AutoPermission()
