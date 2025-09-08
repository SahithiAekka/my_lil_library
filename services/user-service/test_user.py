import pytest
from app import app, db, User # Assuming app, db, and User are accessible from app.py
from werkzeug.security import generate_password_hash # Will be needed for password hashing

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register_user_success(client):
    response = client.post(
        '/register',
        json={
            'username': 'newuser',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
    )
    assert response.status_code == 201
    assert "User registered successfully" in response.json['message']
    assert response.json['data']['username'] == 'newuser'

def test_register_existing_user(client):
    # Register first user
    client.post(
        '/register',
        json={
            'username': 'testuser',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Try to register again with same username
    response = client.post(
        '/register',
        json={
            'username': 'testuser',
            'password': 'anotherpassword',
            'first_name': 'Another',
            'last_name': 'User'
        }
    )
    assert response.status_code == 400
    assert "Username already exists" in response.json['message']

def test_register_missing_fields(client):
    response = client.post(
        '/register',
        json={
            'username': 'incomplete',
            'password': '123'
        }
    )
    assert response.status_code == 400
    assert "Username, password, first_name, and last_name are required" in response.json['message']

def test_login_user_success(client):
    # Register a user first
    hashed_password = generate_password_hash('securepassword')
    user = User(username='loginuser', password=hashed_password, first_name='Login', last_name='User')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    response = client.post(
        '/login',
        json={'username': 'loginuser', 'password': 'securepassword'}
    )
    assert response.status_code == 200
    assert "Login successful" in response.json['message']
    assert 'token' in response.json
    assert response.json['user']['username'] == 'loginuser'

def test_login_incorrect_password(client):
    # Register a user first
    hashed_password = generate_password_hash('correctpassword')
    user = User(username='wrongpassuser', password=hashed_password, first_name='Wrong', last_name='Pass')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    response = client.post(
        '/login',
        json={'username': 'wrongpassuser', 'password': 'incorrectpassword'}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json['message']

def test_login_nonexistent_user(client):
    response = client.post(
        '/login',
        json={'username': 'nonexistent', 'password': 'anypassword'}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json['message']
    
    