from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User

users_blueprint = Blueprint('users', __name__)

class UsersAPI(MethodView):

    def get(self):
        users = User.query.all()
        users_list = [user.email for user in users]
        responseObject = {
            'status': 'success',
            'message': 'Request successful.',
            'users': users_list
        }
        return make_response(jsonify(responseObject)), 201

# define the API resources
users_view = UsersAPI.as_view('users_api')

# add Rules for API Endpoints
users_blueprint.add_url_rule(
    '/users/index',
    view_func=users_view,
    methods=['GET']
)