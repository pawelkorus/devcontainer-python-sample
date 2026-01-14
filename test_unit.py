import pytest
from app import app, db, Trivia


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_create_trivia_success(client):
    """Test creating a trivia entry with valid data"""
    data = {
        'question': 'What is the capital of France?',
        'answer': 'Paris',
        'category': 'Geography',
        'difficulty': 'easy'
    }
    
    response = client.post('/api/trivia', json=data)
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['question'] == data['question']
    assert json_data['answer'] == data['answer']
    assert json_data['category'] == data['category']
    assert json_data['difficulty'] == data['difficulty']
    assert 'id' in json_data
    assert 'created_at' in json_data


def test_create_trivia_minimal(client):
    """Test creating a trivia entry with only required fields"""
    data = {
        'question': 'What is 2+2?',
        'answer': '4'
    }
    
    response = client.post('/api/trivia', json=data)
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['question'] == data['question']
    assert json_data['answer'] == data['answer']
    assert json_data['category'] is None
    assert json_data['difficulty'] is None


def test_create_trivia_missing_required_fields(client):
    """Test creating trivia without required fields"""
    data = {
        'question': 'What is the capital of France?'
        # Missing 'answer'
    }
    
    response = client.post('/api/trivia', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'required' in json_data['error'].lower()


def test_create_trivia_no_json(client):
    """Test creating trivia without JSON data"""
    response = client.post('/api/trivia', data='not json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data


def test_get_trivia(client):
    """Test retrieving a trivia entry by ID"""
    # First create a trivia
    data = {
        'question': 'What is the capital of France?',
        'answer': 'Paris'
    }
    create_response = client.post('/api/trivia', json=data)
    trivia_id = create_response.get_json()['id']
    
    # Then retrieve it
    response = client.get(f'/api/trivia/{trivia_id}')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == trivia_id
    assert json_data['question'] == data['question']
    assert json_data['answer'] == data['answer']


def test_get_trivia_not_found(client):
    """Test retrieving a non-existent trivia entry"""
    response = client.get('/api/trivia/999')
    
    assert response.status_code == 404


def test_list_trivia(client):
    """Test listing all trivia entries"""
    # Create multiple trivia entries
    trivia_data = [
        {'question': 'Q1', 'answer': 'A1'},
        {'question': 'Q2', 'answer': 'A2'},
        {'question': 'Q3', 'answer': 'A3'}
    ]
    
    for data in trivia_data:
        client.post('/api/trivia', json=data)
    
    # List all trivia
    response = client.get('/api/trivia')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 3
    assert all('id' in item for item in json_data)
    assert all('question' in item for item in json_data)


def test_list_trivia_empty(client):
    """Test listing trivia when database is empty"""
    response = client.get('/api/trivia')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == []


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
