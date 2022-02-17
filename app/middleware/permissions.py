'''Add Permissions'''
from functools import wraps
from flask import make_response, jsonify
from flask_jwt_extended import get_jwt_identity
from ..models.User import User, UserCatgoryEnum
from ..models.Application import Application


def only_HR(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        user = User.query.filter_by(UserEmailAddress=get_jwt_identity()).first()
        if user.UserCategory != UserCatgoryEnum.HR:
            return make_response(jsonify({'message':"You don't have permission to carryout this task"}),403)
        return function(*args, **kwargs)
    return wrapper
