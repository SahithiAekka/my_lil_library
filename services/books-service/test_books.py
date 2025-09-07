import requests
import json

def test_get_book_1():
    book_1 = requests.get('http://localhost:5000/books/1')
    assert book_1.status_code == 200, f"Expected status code 200, got {book_1.status_code}"

    expected_output = {
      "author": "George Orwell",
      "available": True,
      "genre": "Dystopian",
      "id": 1,
      "title": "1984"
    }

    assert book_1.json() == expected_output, f"Expected {expected_output}, got {book_1.json()}"  
  