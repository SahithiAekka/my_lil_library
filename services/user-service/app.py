import os 
import jwt  
from flask import Flask, jsonify, request
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'simple-secret-for-testing')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users' 
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Create tables
# with app.app_context(): # This line is removed as per the edit hint
#     db.create_all()

# Home route 
@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, Welcome to User Service!")

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not username or not password or not first_name or not last_name:
        return jsonify(message="Username, password, first_name, and last_name are required to register"), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(message="Username already exists. Please choose a different username."), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Create new user
    new_user = User(
        username=username, 
        password=hashed_password,
        first_name=first_name,
        last_name=last_name
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(message="User registered successfully", 
                   data={
        'username': new_user.username,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'created_at': new_user.created_at.isoformat()
    }), 201

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify(message="Username and password are required to login"), 400
    
    # Find user
    user = User.query.filter_by(username=username).first() # Retrieve user by username only
    
    if not user or not check_password_hash(user.password, password):
        return jsonify(message="Invalid username or password"), 401
        
    # Generate JWT token
    token = jwt.encode({
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    }), 200

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if not users:
        return jsonify(message="No users yet!"), 200 # Return 200 OK with a message
    return jsonify([{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created_at': user.created_at.isoformat()
    } for user in users])

# Get user by username
@app.route('/users/<string:username>', methods=['GET'])
def get_user(username):
    user = User.query.get(username)
    if user:
        return jsonify({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': user.created_at.isoformat()
        })
    return jsonify(message="User not found"), 404

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ensure tables are created when running the app directly
    app.run(host="0.0.0.0", port=5001, debug=True)