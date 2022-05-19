from typing import Dict

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from denied import Ability
from denied.errors import UnauthorizedError
from denied.ext.fastapi import authorize_factory

from .common import ProjectPermissions, UserPolicy

"""
Run this example with : `uvicorn examples.fastapi:app`.
Then you can use curl to test the endpoint :
- `curl http://127.0.0.1:8000/projects/1` => ok
- `curl http://127.0.0.1:8000/projects/2` => unauthorized

FastAPI is based on dependency injection therefore we can use this system to
to get the ability.
First define a function that returns the Ability object. This function can receive all
the predefined objects that FastAPI can inject (ex: the request) and can have its own
dependencies (through `Depends` objects).

Then use `authorize_factory()` to create the `@authorize()` decorator, and use it for
the endpoints methods.
"""

app = FastAPI()


def get_ability(request: Request) -> Ability:
    return Ability(policy=UserPolicy())


authorize = authorize_factory(get_ability)


@app.get("/projects/{id}")
@authorize(ProjectPermissions.view)
async def get(id: int) -> Dict[str, int]:
    return {"id": id}


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: Exception):
    return JSONResponse(content=jsonable_encoder({"error": str(exc)}), status_code=403)
