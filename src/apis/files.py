
from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields

from core import file_utils as FileUtils

api = Namespace('files', description='HIDS files generate')

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

model_populate = api.model(
    'Populate Files', {
        'replicas': fields.Integer(
            required=True,
            min=1,
            max=3,
            default=3,
            description="Number of replicas for HIDS"
        ),
        'files': fields.Integer(
            required=True,
            min=1,
            default=10,
            description="Number of files"
        ),
    })


@api.route("/")
class Files(Resource):
    @api.doc(description="Check file")
    @api.response(200, "File checked")
    @api.response(400, "Verification fail")
    @api.expect(model_populate)
    def get(self):
        # if bool(json_files):
        #     json_files = FileUtils.
        return "{hola: mundo}"


@api.route("/populate")
class Populate(Resource):
    @api.doc(description="Check file")
    @api.response(200, "File checked")
    @api.response(400, "Verification fail")
    @api.expect(model_populate)
    def post(self):
        num_replicas = request.json["replicas"]
        num_files = request.json["files"]
        json_files = FileUtils.file_generator(
            self.api.app.root_path,
            num_replicas,
            num_files
        )
        return json_files
