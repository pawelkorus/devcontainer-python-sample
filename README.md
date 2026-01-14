# Flask Trivia API

A RESTful API for managing trivia questions built with Flask and SQLAlchemy.

## Features

- Create, read, and list trivia questions
- Store trivia with question, answer, category, and difficulty
- Health check endpoint
- Unit and integration tests
- DevContainer support for consistent development environment

## Prerequisites

- Python 3.11+
- pip (Python package manager)
- Docker (optional, for DevContainer)

## Installation

### Using DevContainer (Recommended)

1. Open the project in VS Code
2. When prompted, click "Reopen in Container"
3. The environment will be automatically set up

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd devcontainer-python-sample
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Using Flask CLI:
```bash
flask run
```

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test files:
```bash
pytest test_unit.py
pytest test_integration.py
```

### Run tests verbosely:
```bash
pytest -v
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns the health status of the API

### Create Trivia
- **POST** `/api/trivia`
  - Creates a new trivia entry
  - **Body** (JSON):
    ```json
    {
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": "Geography",
      "difficulty": "easy"
    }
    ```
  - **Required fields**: `question`, `answer`
  - **Optional fields**: `category`, `difficulty`

### Get Trivia by ID
- **GET** `/api/trivia/<id>`
  - Retrieves a specific trivia entry by ID

### List All Trivia
- **GET** `/api/trivia`
  - Returns a list of all trivia entries

## Development

### Database

By default, the application uses SQLite (`trivia.db`). To use a different database, set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Code Formatting

The project uses Black for code formatting. Format code with:

```bash
black .
```

### Linting

The project uses Flake8 for linting. Run linting with:

```bash
flake8 .
```

## Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///trivia.db`)
- `FLASK_APP`: Flask application file (default: `app.py`)
- `FLASK_ENV`: Flask environment (default: `development`)

## License

This project is licensed under the MIT License.
