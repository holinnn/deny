from typing import Tuple

from flask import Flask, g, jsonify
from flask.wrappers import Response

from deny.errors import UnauthorizedError
from deny.ext.flask import authorize
from deny.sync import Ability

from .common import ProjectPermissions, SyncUserPolicy

"""
Run this example with : `FLASK_APP=examples.flask:app flask run`.
Then you can use curl to test the endpoint :
- `curl http://127.0.0.1:5000/projects/1` => ok
- `curl http://127.0.0.1:5000/projects/2` => unauthorized

The @authorize() decorator expects an `ability` property on the request's context.
Therefore a middleware (see the `inject_ability()`) must add the Ability object into
this context.
The `ability` property can be named something else, but it will have to be specified
in the decorator (`@authorize(ProjectPermissions.view, ability_key="...")`).
"""


app = Flask("example")


@app.before_request
def inject_ability() -> None:
    g.ability = Ability(policy=SyncUserPolicy())


@app.get("/projects/<int:id>")
@authorize(ProjectPermissions.view)
def get(id: int) -> Response:
    return jsonify({"id": id})


@app.errorhandler(UnauthorizedError)
def unauthorized_handler(exc: Exception) -> Tuple[Response, int]:
    return jsonify({"error": str(exc)}), 403
