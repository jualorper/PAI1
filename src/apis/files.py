
from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields

api = Namespace('teams', description='Gestion Teams asociados ALM')

model = api.model(
    'Request',
    {
        'token': fields.String(
            required=True,
            description="User token",
            help="Token cannot be blank."
        ),
        'hash': fields.String(
            required=True,
            description="Hash of file",
            help="Hash cannot be blank."
        ),
        'filename': fields.String(
            required=True,
            description="filename",
            help="Filename cannot be blank."
        )
    }
)

model_return = api.model(
    'Response', {
        'hash': fields.String(description="Hash of file"),
        'MAC': fields.String(description="Message Authentication Code"),
    })


@api.route("/")
class Teams(Resource):
    @api.doc(description="Check file")
    @api.response(200, "File checked", model=model_return)
    @api.response(400, "Verification fail", model=model_return)
    @api.expect(model)
    def post(self):
        response = "{hola: mundo}"
        return response
