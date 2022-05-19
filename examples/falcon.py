from typing import Any, Dict

import falcon
from falcon import Request, Response, asgi

from denied import Ability
from denied.errors import UnauthorizedError
from denied.ext.falcon import authorize

from .common import ProjectPermissions, UserPolicy

"""
Run this example with : `uvicorn examples.falcon:app`.
Then you can use curl to test the endpoint :
- `curl http://127.0.0.1:8000/projects/1` => ok
- `curl http://127.0.0.1:8000/projects/2` => unauthorized


The @authorize() decorator expects an `ability` property on the request's context.
Therefore a middleware (see the AbilityMiddleware) must add the Ability object into
this context.
The `ability` property can be named something else, but it will have to be specified
in the decorator (`@authorize(ProjectPermissions.view, ability_key="...")`).
"""


class AbilityMiddleware:
    async def process_request(self, req: Request, _: Response) -> None:
        req.context["ability"] = Ability(policy=UserPolicy())


class ErrorHandler:
    async def __call__(
        self, req: Request, resp: Response, error: Exception, params: Dict[str, Any]
    ) -> None:
        resp.status = falcon.HTTP_403
        resp.media = {"error": str(error)}


class ProjectResource:
    @authorize(ProjectPermissions.view)
    async def on_get(self, req: Request, resp: Response, id: int) -> None:
        resp.media = {"id": id}


app = asgi.App()
app.add_middleware(AbilityMiddleware())
app.add_error_handler(UnauthorizedError, ErrorHandler())
app.add_route("/projects/{id:int}", ProjectResource())
