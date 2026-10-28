from flask import Blueprint ,request,jsonify
from flask_jwt_extended import create_access_token
from extensions import db,jwt
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register',methods =['POST'])
def register():
    data= request.get_json()

    if not data:
        return jsonify({"error":"No data provided"}),400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error":"Email already exists"}),409
    new_user =User(name=data["name"], email=data["email"])
    
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message":"User Register Sucessfully"}),201

@auth_bp.route('/auth/login',methods=['POST'])
def login():
    data=request.get_json()

    if not data:
        return jsonify({"error":"No data is Found"}),400
    
    if not data.get("email") or not data.get("password"):
        return jsonify({"error":"Email and Password are requried"}),400
    user=User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error":"Invalid Credential"}),401
    

    token=create_access_token(identity=str(user.id))

    return jsonify({"message":"Login Sucessfully","token":token}),200
    
    