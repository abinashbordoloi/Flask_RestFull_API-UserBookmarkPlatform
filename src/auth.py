from flask import Blueprint, request
from  werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import validators
from src.database import User,db

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post("/register")
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']


    if len(password)<6 or password.isalnum()==False :
        return jsonify({'error': 'Password must be atleast 6 characters long and should contain alpha numeric characters'})
    
    if not  username.isalnum() or " " in username:
        return jsonify({'error': 'Username should be alphanumeric and should not contain spaces'})

    if not validators.email(email):
        return jsonify({'error': 'Invalid Email'})
    

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email is Taken, Please enter a different email'})
    if User.query.filter_by(username = username).first() is not None:
        return jsonify({'error': 'Username is Taken, Please enter a different username'})
    


    password_hash = generate_password_hash(password)
    user = User(username = username, password = password_hash, email = email)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Created",
                    'user': {"username": username,
                    'email': email
                    }})

                
 

@auth.post('/login')
def login():
    email = request.json.get('email', "")
    password = request.json.get('password', "")

    user = User.query.filter_by(email=email).first()
    if user:
        valid_password = check_password_hash(user.password, password)
        if valid_password:
            refresh = create_refresh_token(identity=user.id)
            access  = create_access_token (identity=user.id)
            return jsonify({'message': 'Login Successful',
                            "tokens":{ 'refresh': refresh,
                            'access': access},
                            'user_details': {'username': user.username,
                            'email': user.email}})
        else:
            return jsonify({'error': 'Invalid Password'})
  
                       



@auth.get("/me")
@jwt_required()
def me():
    return {'user': 'me'}
