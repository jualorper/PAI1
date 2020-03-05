
from functools import wraps

from flask import request
from flask_restplus import Namespace, Resource, fields

from core.file_utils import FileUtils

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY',
    }
}

api = Namespace(
    'file',
    description='HIDS files generate',
    authorizations=authorizations
)


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
    }
)

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
    }
)

model_mac = api.model(
    'Generate mac', {
        'token': fields.String(
            required=True,
            description="User token"
        ),
        'filename': fields.String(
            required=True,
            description="Name of file"
        ),
        'hash': fields.String(
            required=True,
            description="Hash of file"
        ),
    }
)


file_utils = FileUtils()


# TOKEN check
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'Token is missing.'}, 401

        tokens = ['miToken']
        if token not in tokens:
            return {'message': 'Not Authorized.'}, 401

        return f(*args, **kwargs)
    return decorated


fileUtils = FileUtils()


@api.route("/")
@api.response(401, "Not Authorized")
class Files(Resource):
    @api.doc(description="Get all files and hashes",
             responses={
                 200: "Files and hashes",
                 500: "HIDS failure. Please populate files"
             })
    # @token_required
    def get(self):
        return file_utils.get_hashes()


@api.route("/<string:filename>")
@api.response(401, "Not Authorized")
class File(Resource):
    @api.doc(description="Get one filename and hash",
             responses={
                 200: "Filename and hash",
                 400: "Filename and hash not found",
             })
    def get(self, filename):
        return file_utils.get_hash(filename)

    @api.doc(description="Get one filename and hash",
             responses={
                 200: "Filename and hash",
                 400: "Filename and hash not found"
             })
    def post(self, filename):
        return fileUtils.get_hash(
            filename,
            request.json["token"],
            request.json["hash"],
        )


@api.route("/populate")
@api.response(401, "Not Authorized")
class Populate(Resource):
    @api.doc(description="Populate dummies files",
             security='apikey',
             responses={
                 201: "Files and replicas created",
                 400: "Error creating files or replicas"
             })
    @api.expect(model_populate)
    # @token_required
    def post(self):
        return file_utils.file_generator(
            request.json["replicas"],
            request.json["files"]
        )


@api.route("/mac")
class Initialize(Resource):
    @api.doc(description="Generate mac")
    @api.expect(model_mac)
    def post(self):
        return file_utils.check_file(
            request.json["filename"],
            request.json["hash"],
            request.json["token"]
        )
