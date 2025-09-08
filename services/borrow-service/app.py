import os
from flask import Flask, jsonify, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Borrow model
class Borrow(db.Model):
    __tablename__ = 'borrows'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    returned = db.Column(db.Boolean, default=False)

# Create tables
# with app.app_context(): # This line is removed as per the edit hint
#     db.create_all()

# Home route
@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, Welcome to Borrow Service!")

# Borrow a book
@app.route('/borrowbook', methods=['POST'])
def borrow_book():
    data = request.json
    username = data.get('username')
    book_id = data.get('book_id')
    
    if not username or not book_id:
        return jsonify(message="Username and book_id are required"), 400
    
    # Check if book is already borrowed (simple check)
    existing_borrow = Borrow.query.filter_by(book_id=book_id, returned=False).first()
    if existing_borrow:
        return jsonify(message="Book is already borrowed"), 409
    
    # Create new borrow record
    new_borrow = Borrow(username=username, book_id=book_id)
    db.session.add(new_borrow)
    db.session.commit()
    
    return jsonify({
        'id': new_borrow.id,
        'username': new_borrow.username,
        'book_id': new_borrow.book_id,
        'borrow_date': new_borrow.borrow_date.isoformat(),
        'returned': new_borrow.returned
    }), 201

# Return a book
@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    username = data.get('username')
    book_id = data.get('book_id')
    
    if not username or not book_id:
        return jsonify(message="Username and book_id are required"), 400
    
    # Find the borrow record
    borrow = Borrow.query.filter_by(username=username, book_id=book_id, returned=False).first()
    if not borrow:
        return jsonify(message="No active borrow found for this user and book"), 404
    
    # Mark as returned
    borrow.returned = True
    db.session.commit()
    
    return jsonify({
        'id': borrow.id,
        'username': borrow.username,
        'book_id': borrow.book_id,
        'borrow_date': borrow.borrow_date.isoformat(),
        'returned': borrow.returned
    }), 200

# Get all borrows
@app.route('/borrows', methods=['GET'])
def get_borrows():
    borrows = Borrow.query.all()
    return jsonify([{
        'id': borrow.id,
        'username': borrow.username,
        'book_id': borrow.book_id,
        'borrow_date': borrow.borrow_date.isoformat(),
        'returned': borrow.returned
    } for borrow in borrows])

# Get borrows for a specific book
@app.route('/borrows/book/<int:book_id>', methods=['GET'])
def get_borrows_by_book(book_id):
    borrows = Borrow.query.filter_by(book_id=book_id).all()
    return jsonify([{
        'id': borrow.id,
        'username': borrow.username,
        'book_id': borrow.book_id,
        'borrow_date': borrow.borrow_date.isoformat(),
        'returned': borrow.returned
    } for borrow in borrows])

# Get borrows for a specific user
@app.route('/borrows/user/<string:username>', methods=['GET'])
def get_borrows_by_user(username):
    borrows = Borrow.query.filter_by(username=username, returned=False).all()
    if not borrows:
        return jsonify(message=f"No active borrows found for user: {username}"), 404
    return jsonify([{
        'id': borrow.id,
        'username': borrow.username,
        'book_id': borrow.book_id,
        'borrow_date': borrow.borrow_date.isoformat(),
        'returned': borrow.returned
    } for borrow in borrows])

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ensure tables are created when running the app directly
    app.run(host="0.0.0.0", port=5002, debug=True)
