from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from models import db, Users

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/myproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

CORS(app, supports_credentials=True)

db.init_app(app)
with app.app_context():
    db.create_all()

ma = Marshmallow(app)


# Marshmallow Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Routes
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/users', methods=['GET'])
def listusers():
    all_users = Users.query.all()
    results = users_schema.dump(all_users)
    return jsonify(results)


@app.route('/userdetails/<id>', methods=['GET'])
def userdetails(id):
    user = Users.query.get(id)
    return user_schema.jsonify(user)


@app.route('/userupdate/<id>', methods=['PUT'])
def userupdate(id):
    user = Users.query.get(id)

    name = request.json['name']
    email = request.json['email']

    user.name = name
    user.email = email

    db.session.commit()
    return user_schema.jsonify(user)


@app.route('/userdelete/<id>', methods=['DELETE'])
def userdelete(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


@app.route('/newuser', methods=['POST'])
def newuser():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    # Hash the password for security
    hashed_password = generate_password_hash(password, method='sha256')

    users = Users(name=name, email=email, password=hashed_password)

    db.session.add(users)
    db.session.commit()
    return user_schema.jsonify(users)

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # Fetch user from the database
    user = Users.query.filter_by(email=email).first()

    # if user:
    #     print(f"User found: {user.email}")
    #     if check_password_hash(user.password, password):
    #         # Successful login
    #         return jsonify({
    #             "message": "Login successful",
    #             "user": {
    #                 "id": user.id,
    #                 "name": user.name,
    #                 "email": user.email
    #             }
    #         }), 200
    #     else:
    #         print("Password mismatch")
    # else:
    #     print("User not found")

    # Invalid credentials
    return jsonify({"message": "Invalid email or password"}), 401


if __name__ == "__main__":
    app.run(debug=True)
