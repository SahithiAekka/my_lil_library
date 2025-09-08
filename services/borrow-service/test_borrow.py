import pytest
from app import app, db, Borrow  # Assuming app, db, and Borrow are accessible from app.py

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_borrow_book_success(client):
    response = client.post(
        '/borrowbook',
        json={'username': 'testuser', 'book_id': 1}
    )
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['username'] == 'testuser'
    assert response.json['book_id'] == 1
    assert response.json['returned'] is False

def test_get_borrows_by_user_no_borrows(client):
    response = client.get('/borrows/user/nonexistentuser')
    assert response.status_code == 404
    assert response.json == {'message': 'No active borrows found for user: nonexistentuser'}

def test_get_borrows_by_user_with_borrows(client):
    # First, borrow a book
    client.post(
        '/borrowbook',
        json={'username': 'testuser', 'book_id': 1}
    )
    
    response = client.get('/borrows/user/testuser')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['username'] == 'testuser'
    assert response.json[0]['book_id'] == 1
    assert response.json[0]['returned'] is False 