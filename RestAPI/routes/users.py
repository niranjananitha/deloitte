# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import jwt_required , get_jwt_identity

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(name=data["name"], email=data["email"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "user": new_user.to_dict()}), 201


@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()

    if not users:
        return jsonify({"message": "No users found"}), 404

    return jsonify([user.to_dict() for user in users]), 200


@users_bp.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


@users_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "email" in data:
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != id:
            return jsonify({"error": "Email already exists"}), 409
        user.email = data["email"]

    if "name" in data:
        user.name = data["name"]

    db.session.commit()

    return jsonify({"message": "User updated", "user": user.to_dict()}), 200


@users_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200

# @users_bp.route('/users',methods=['GET'])
# @jwt_required()

# def get_all_users():
#     users =User.query.all()

#     if not users:
#         return jsonify({"message": "No Users found "}),404

#     return jsonify([user.to_dict() for user in users]),200