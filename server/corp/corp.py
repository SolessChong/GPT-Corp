# corp/corp.py

from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import check_password_hash
from app_common import common
from models.basic_models import User, Corp

# Assuming common.db is the SQLAlchemy instance from app_common.py
# and common.jwt is the JWTManager instance

corp_blueprint = Blueprint('corp', __name__)

@corp_blueprint.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({"message": "Unauthorized"}), 403

    users = User.query.filter_by(corp_id=current_user.corp_id).all()
    users_list = [{'id': user.id, 'username': user.username, 'balance': user.balance} for user in users]

    return jsonify(users_list), 200

@corp_blueprint.route('/my_corp', methods=['GET'])
@jwt_required()
def get_corp():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({"message": "User not found"}), 404

    corp = Corp.query.filter_by(id=current_user.corp_id).first()
    if not corp:
        return jsonify({"message": "Corporation not found"}), 404

    corp_details = {
        'id': corp.id,
        'name': corp.name,
        'balance': corp.balance,
        'logo': corp.logo
    }

    return jsonify(corp_details), 200


@corp_blueprint.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_balance():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    recipient_id = data.get('recipient_id')
    amount = data.get('amount')

    if current_user.transfer_balance(recipient_id, amount):
        return jsonify({"message": "Transfer successful"}), 200
    else:
        return jsonify({"message": "Transfer failed"}), 400

# corp/corp.py
@corp_blueprint.route('/corp_admin', methods=['GET'])
@jwt_required(optional=True)
def corp_admin():
    current_user_id = get_jwt_identity()
    users = []
    if current_user_id:
        current_user = User.query.get(current_user_id)
        # Check if the current user is an admin and has a corp_id
        if current_user and current_user.is_admin and current_user.corp_id:
            users = User.query.filter_by(corp_id=current_user.corp_id).all()

    return render_template('corp_admin.html', users=users)


# Register the blueprint in your factory function in app_common.py
# app.register_blueprint(corp_blueprint, url_prefix='/corp')

