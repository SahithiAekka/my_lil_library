import os
from flask import Flask, jsonify, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Book model
class Book(db.Model):
    __tablename__ = 'books' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    available = db.Column(db.Boolean, default=True)
    
    
    @property
    def is_available(self):
        # Make HTTP request to borrow service
        # import requests
        try:
            response = requests.get(f'http://borrow-service:5002/borrows/book/{self.id}')
            if response.status_code == 200:
                borrows = response.json()
                # Check if any active borrows exist
                for borrow in borrows:
                    if not borrow.get('returned', False):
                        return False
            return True
        except:
            return True  # Default to available if service is down

# home route 
@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, Welcome to my little libary!")

# get all the books 
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'available': book.is_available
    } for book in books])

# get a specific book by id
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'available': book.is_available
        })
    return jsonify(message="Book not found :( "), 404

# get a specific book by genre
@app.route('/books/<string:genre>', methods=['GET'])
def get_books_by_genre(genre):
    books = Book.query.filter(Book.genre.ilike(f'%{genre}%')).all()
    if books:
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'available': book.is_available
        } for book in books])
    return jsonify(message="No books found in this genre :( "), 404

# Add a new book
@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    new_book = Book(
        title=data.get("title"),
        author=data.get("author"),
        genre=data.get("genre"),
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({
        'id': new_book.id,
        'title': new_book.title,
        'author': new_book.author,
        'genre': new_book.genre,
        'available': new_book.is_available
    }), 201

# Update book availability
@app.route("/books/<int:book_id>", methods=["PUT"])     
def update_book_availability(book_id):
    data = request.json
    book = Book.query.get(book_id)
    if book:
        # This logic needs to be updated to reflect the new Borrow model
        # For now, we'll just return the current state
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'available': book.is_available
        })
    return jsonify(message="Book not found :( "), 404

# Delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify(message="Book deleted successfully"), 200
    return jsonify(message="Book not found"), 404

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)