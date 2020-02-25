from flask_restplus import Api
from .files import api as api_file

api = Api(
    title="PAI1",
    description="Proof of Possession",
    version="1.0",
)

api.add_namespace(api_file)
