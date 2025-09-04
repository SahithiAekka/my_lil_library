from flask import Flask, jsonify, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# temporary in-memory storage for books
books = [
    {'id': 1, 'title': '1984', 'author': 'George Orwell', 'genre': 'Dystopian','available': True},
    {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'genre': 'Fiction','available': True},
    {'id': 3, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'genre': 'Classic','available': False},
    {'id': 4, 'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'genre': 'Fiction','available': True},
    {'id': 5, 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'genre': 'Romance','available': False},
    {'id': 6, 'title': 'The Hobbit', 'author': 'J.R.R. Tolkien', 'genre': 'Fantasy','available': True},
    {'id': 7, 'title': 'Fahrenheit 451', 'author': 'Ray Bradbury', 'genre': 'Dystopian','available': True},
]
        
# home route 
@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, Welcome to my little libary!")

# get all the books 
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books) 

# get a specific book by id
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify(message="Book not found :( "), 404

# get a specific book by genre
@app.route('/books/<string:genre>', methods=['GET'])
def get_books_by_genre(genre):
    genre_books = [book for book in books if book['genre'].lower() == genre.lower()]
    if genre_books:
        return jsonify(genre_books)
    return jsonify(message="No books found in this genre :( "), 404

# Add a new book
@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data.get("title"),
        "author": data.get("author"),
        "genre": data.get("genre"),
        "available": True
    }
    books.append(new_book)
    return jsonify(new_book), 201 

# Update book availability
@app.route("/books/<int:book_id>", methods=["PUT"])     
def update_book_availability(book_id):
    data = request.json
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        book['available'] = data.get('available', book['available'])
        return jsonify(book)
    return jsonify(message="Book not found :( "), 404

# Delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    books = [book for book in books if book['id'] != book_id]
    return jsonify(message="Book deleted successfully"), 200

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    

