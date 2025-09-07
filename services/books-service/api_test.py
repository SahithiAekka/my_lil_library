import requests
import json

book_1= requests.get('http://localhost:5000/books/1')
assert book_1.status_code==200, "Request failed"
print(book_1.json())

expected_output={
  "author": "George Orwell",
  "available": True,
  "genre": "Dystopian",
  "id": 1,
  "title": "1984"
}

if book_1.json()==expected_output:
    print("Test Successfull")
else:
    print("Test Failed")
    
