from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from deny import Ability
from deny.errors import UnauthorizedError
from deny.ext.sanic import authorize

from .common import ProjectPermissions, UserPolicy

"""
Run this example with : `uvicorn examples.sanic:app`.
Then you can use curl to test the endpoint :
- `curl http://127.0.0.1:8000/projects/1` => ok
- `curl http://127.0.0.1:8000/projects/2` => unauthorized

The @authorize() decorator expects an `ability` property on the request's context.
Therefore a middleware (see the `inject_ability()`) must add the Ability object into
this context.
The `ability` property can be named something else, but it will have to be specified
in the decorator (`@authorize(ProjectPermissions.view, ability_key="...")`).
"""


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
