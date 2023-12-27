from flask import Blueprint

user_blueprint = Blueprint('user', __name__)

from flask_jwt_extended import get_jwt_identity, jwt_required
from models.basic_models import User
from flask import jsonify

@user_blueprint.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # If the current user is not an admin or the requested user, deny access
    if not current_user.is_admin and current_user_id != user_id:
        return jsonify({"message": "Access denied"}), 403

    user = User.query.get(user_id)
    if user:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.active,
            'corp_id': user.corp_id,
            'is_admin': user.is_admin,
            'balance': user.balance,
            'tokens_used': user.tokens_used
            # Do not include sensitive information like password_hash
        }
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "User not found"}), 404