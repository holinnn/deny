# deny

Library for managing permissions in your Python 3.7+ projects.  
For example, it can be used to grant access to some API endpoints based on policies you defined.

## Installation

```
pip install deny
```

## Usage

First define the permissions needed in your project:

```python 
from deny import AutoPermission, Permission

class ProfilePermissions:
    view = Permission(name="view_project")
    edit = AutoPermission()  # name will be automatically set to "ProjectPermissions.edit"

class SessionPermissions:
    create = AutoPermission()
    delete = AutoPermission()
```

Then create policies that will be used to grant the permissions:

```python
from deny import Policy, authorize

class LoggedInUser:
    @authorize(SessionPermissions.delete)
    async def can_logout(self):
        return True


class AnonymousUser(Policy):
    @authorize(SessionPermissions.create)
    async def can_logout(self):
        return True


class UserPolicy(LoggedInUser, Policy):
    def __init__(self, current_user_id: int):
        """You should inject any dependency this policy relies on.
        Here we just save the current user ID, but you might need 
        a connection to a database, a whole user object, etc.
        """
        self._current_user_id = current_user_id

    @authorize(ProfilePermissions.edit)
    async def can_edit_profile(self, user_id: int) -> bool:
        """Only current user can edit his own profile."""
        return self._current_user_id == user_id

    @authorize(ProfilePermissions.view)
    async def can_view_profile(self, user_id: int) -> bool:
        """Everybody can view the user profiles."""
        return True
```

Finally create an Ability with the right policy and check if the permissions are granted:

```python
from deny import Ability

def get_ability(current_user_id: Optional[int]) -> Ability:
    if current_user_id:
        policy = UserPolicy(current_user_id)
    else:
        policy = AnonymousUser()

    return Ability(policy=policy)

################
# Logged in user
ability = get_ability(1)
await ability.can(ProfilePermissions.view, 1) # True
await ability.can(ProfilePermissions.view, 2) # True
await ability.can(ProfilePermissions.edit, 1) # True
await ability.authorize(ProfilePermissions.edit, 1) # does not throw any error
await ability.can(ProfilePermissions.edit, 2) # False
await ability.authorize(ProfilePermissions.edit, 2) # throw an UnauthorizedError
await ability.can(SessionPermission.create) # False
await ability.can(ProfilePermissions.delete) # True

################
# Anonymous user
ability = get_ability(None)
await ability.can(ProfilePermissions.view, 1) # False
await ability.can(ProfilePermissions.view, 2) # False
await ability.can(ProfilePermissions.edit, 1) # False
await ability.authorize(ProfilePermissions.edit, 1) # throw an UnauthorizedError
await ability.can(ProfilePermissions.edit, 2) # False
await ability.authorize(ProfilePermissions.edit, 2) # throw an UnauthorizedError
await ability.can(SessionPermission.create) # True
await ability.can(ProfilePermissions.delete) # False
```

You can see the full example in [examples/usage.py](https://github.com/holinnn/deny/tree/main/examples/usage.py) (you will need `asyncio` to run it, `pip install asyncio`)


## Web frameworks

Deny can be used with any web framework.  
But it comes with some helper functions for [Falcon](https://falcon.readthedocs.io/en/stable/), [Sanic](https://sanic.dev/en/) and [FastAPI](https://fastapi.tiangolo.com/).

Here is an example for the [Sanic](https://sanic.dev/en/) web framework:
```python 
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from typing import Any

from deny import Ability, AutoPermission, Policy, authorize as policy_authorize
from deny.errors import UnauthorizedError
from deny.ext.sanic import authorize



class ProjectPermissions:
    view = AutoPermission()


class UserPolicy(Policy):
    @authorize(ProjectPermissions.view)
    async def can_view_project(self, request: Request, id: int) -> bool:
        return id == 1


app = Sanic("example")


@app.middleware("request")
async def inject_ability(request: Request) -> None:
    request.ctx.ability = Ability(policy=UserPolicy())


@app.get("/projects/<id:int>")
@authorize(ProjectPermissions.view)
async def get(request: Request, id: int) -> HTTPResponse:
    return json({"id": id})


@app.exception(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: Exception):
    return json({"error": str(exc)}, status=403)
```

You can find the examples for each of those frameworks in the [examples/](https://github.com/holinnn/deny/tree/main/examples) folder from this repository.


## Sync support

By default all the classes provided by `deny` are built to run in an asynchronous environement.  
If you run in a synchronous environement (without `async`, `await`), then import from `deny.sync` instead of `deny`.  
See [examples/sync.py](https://github.com/holinnn/deny/tree/main/examples/sync.py) for a full example.

