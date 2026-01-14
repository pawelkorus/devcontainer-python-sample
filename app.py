from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///trivia.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Trivia(db.Model):
    """Model for storing trivia questions"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty,
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
            )
        }


@app.route('/api/trivia', methods=['POST'])
def create_trivia():
    """Create a new trivia entry"""
    try:
        # Try to get JSON data, return 400 if parsing fails
        try:
            data = request.get_json(force=True)
        except (BadRequest, ValueError, TypeError):
            return jsonify({'error': 'Invalid JSON data'}), 400

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required fields
        if 'question' not in data or 'answer' not in data:
            return jsonify({'error': 'question and answer are required'}), 400

        # Create new trivia entry
        trivia = Trivia(
            question=data['question'],
            answer=data['answer'],
            category=data.get('category'),
            difficulty=data.get('difficulty')
        )

        db.session.add(trivia)
        db.session.commit()

        return jsonify(trivia.to_dict()), 201

    except (BadRequest, ValueError, TypeError):
        # Handle invalid JSON or parsing errors
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/trivia/<int:trivia_id>', methods=['GET'])
def get_trivia(trivia_id):
    """Get a trivia entry by ID"""
    trivia = db.session.get(Trivia, trivia_id)
    if trivia is None:
        return jsonify({'error': 'Trivia not found'}), 404
    return jsonify(trivia.to_dict())


@app.route('/api/trivia', methods=['GET'])
def list_trivia():
    """List all trivia entries"""
    trivia_list = Trivia.query.all()
    return jsonify([trivia.to_dict() for trivia in trivia_list])


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
