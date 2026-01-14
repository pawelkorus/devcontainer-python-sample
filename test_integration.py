import pytest
from testcontainers.postgres import PostgresContainer
from app import app, db, Trivia


@pytest.fixture(scope='module')
def postgres_container():
    """Create a PostgreSQL test container"""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope='module')
def test_app(postgres_container):
    """Create Flask app with PostgreSQL database from testcontainer"""
    # Get connection string from container
    database_url = postgres_container.get_connection_url()

    # Configure app with test database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create tables
    with app.app_context():
        db.create_all()

    yield app

    # Cleanup
    with app.app_context():
        db.drop_all()


@pytest.fixture
def clean_db(test_app):
    """Clean the database before each test"""
    with test_app.app_context():
        db.session.query(Trivia).delete()
        db.session.commit()
    yield
    # Optional: clean after test as well
    with test_app.app_context():
        db.session.query(Trivia).delete()
        db.session.commit()


@pytest.fixture
def client(test_app, clean_db):
    """Create a test client"""
    with test_app.test_client() as client:
        yield client


def test_create_trivia_integration(client):
    """Integration test: Create trivia and verify it persists"""
    data = {
        'question': 'What is the largest planet in our solar system?',
        'answer': 'Jupiter',
        'category': 'Astronomy',
        'difficulty': 'medium'
    }

    # Create trivia
    response = client.post('/api/trivia', json=data)
    assert response.status_code == 201
    created_trivia = response.get_json()
    trivia_id = created_trivia['id']

    # Verify it was saved by retrieving it
    get_response = client.get(f'/api/trivia/{trivia_id}')
    assert get_response.status_code == 200
    retrieved_trivia = get_response.get_json()

    assert retrieved_trivia['question'] == data['question']
    assert retrieved_trivia['answer'] == data['answer']
    assert retrieved_trivia['category'] == data['category']
    assert retrieved_trivia['difficulty'] == data['difficulty']


def test_multiple_trivia_persistence(client):
    """Integration test: Create multiple trivia entries and verify they
    all persist"""
    trivia_entries = [
        {'question': 'What is 2+2?', 'answer': '4',
            'category': 'Math', 'difficulty': 'easy'},
        {'question': 'What is the capital of Japan?', 'answer': 'Tokyo',
            'category': 'Geography', 'difficulty': 'medium'},
        {'question': 'Who wrote Romeo and Juliet?',
            'answer': 'William Shakespeare',
            'category': 'Literature', 'difficulty': 'hard'}
    ]

    created_ids = []
    for entry in trivia_entries:
        response = client.post('/api/trivia', json=entry)
        assert response.status_code == 201
        created_ids.append(response.get_json()['id'])

    # List all trivia
    list_response = client.get('/api/trivia')
    assert list_response.status_code == 200
    all_trivia = list_response.get_json()

    assert len(all_trivia) == 3

    # Verify each entry can be retrieved individually
    for i, trivia_id in enumerate(created_ids):
        get_response = client.get(f'/api/trivia/{trivia_id}')
        assert get_response.status_code == 200
        retrieved = get_response.get_json()
        assert retrieved['question'] == trivia_entries[i]['question']
        assert retrieved['answer'] == trivia_entries[i]['answer']


def test_trivia_with_special_characters(client):
    """Integration test: Create trivia with special characters and unicode"""
    data = {
        'question': 'What is the chemical formula for water? (H₂O)',
        'answer': 'H₂O',
        'category': 'Science',
        'difficulty': 'easy'
    }

    response = client.post('/api/trivia', json=data)
    assert response.status_code == 201
    trivia_id = response.get_json()['id']

    # Retrieve and verify special characters are preserved
    get_response = client.get(f'/api/trivia/{trivia_id}')
    assert get_response.status_code == 200
    retrieved = get_response.get_json()
    assert retrieved['question'] == data['question']
    assert retrieved['answer'] == data['answer']


def test_trivia_long_text(client):
    """Integration test: Create trivia with long text fields"""
    data = {
        'question': (
            'What is a very long question that tests the database '
            'field length limits? ' * 5
        ),
        'answer': (
            'This is a very long answer that also tests the database '
            'field length limits. ' * 5
        ),
        'category': 'Test Category',
        'difficulty': 'hard'
    }

    response = client.post('/api/trivia', json=data)
    assert response.status_code == 201
    trivia_id = response.get_json()['id']

    # Verify long text is stored correctly
    get_response = client.get(f'/api/trivia/{trivia_id}')
    assert get_response.status_code == 200
    retrieved = get_response.get_json()
    assert len(retrieved['question']) > 100
    assert len(retrieved['answer']) > 100
