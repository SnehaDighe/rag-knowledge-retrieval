"""
Flask backend for RAG Knowledge Retrieval System
"""
import os
import logging
import tempfile
import shutil
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import RAG components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.main import KnowledgeRetrievalSystem
from src.data_ingestion import DataIngestion

load_dotenv()

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt_manager = JWTManager(app)

logger = logging.getLogger(__name__)

# Simple in-memory user store (replace with database in production)
users = {}

# Initialize RAG system
rag_system = None
documents_count = 0
embeddings_count = 0

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def initialize_rag_system():
    """Initialize the RAG system"""
    global rag_system, documents_count, embeddings_count
    try:
        logger.info("Initializing RAG system...")
        rag_system = KnowledgeRetrievalSystem()
        rag_system.initialize()

        # Count documents and embeddings
        data_path = rag_system.data_path
        ingestion = DataIngestion(data_path)
        docs = ingestion.ingest_text_files()
        chunks = ingestion.chunk_documents(rag_system.chunk_size, rag_system.overlap)

        documents_count = len(docs)
        embeddings_count = len(chunks)

        logger.info(f"RAG system initialized with {documents_count} documents and {embeddings_count} embeddings")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return False

# Initialize on startup
init_success = initialize_rag_system()

# Authentication Routes
@app.route('/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        if username in users:
            return jsonify({'error': 'Username already exists'}), 409

        # Hash password and store user
        hashed_password = hash_password(password)
        users[username] = {
            'password': hashed_password,
            'created_at': datetime.utcnow().isoformat()
        }

        logger.info(f"User {username} registered successfully")
        return jsonify({
            'message': 'User created successfully',
            'username': username
        }), 201
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        if username not in users:
            return jsonify({'error': 'Invalid username or password'}), 401

        user = users[username]
        if not check_password(password, user['password']):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Create JWT token
        access_token = create_access_token(identity=username)

        logger.info(f"User {username} logged in successfully")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        }), 200
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        current_user = get_jwt_identity()
        return jsonify({
            'valid': True,
            'user': current_user,
            'message': 'Token is valid'
        }), 200
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return jsonify({'error': 'Invalid token'}), 401


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    global rag_system

    health_status = {
        'status': 'healthy' if rag_system else 'unhealthy',
        'service': 'RAG Knowledge Retrieval System',
        'rag_system_initialized': rag_system is not None,
        'openai_api_available': bool(os.getenv('OPENAI_API_KEY'))
    }

    status_code = 200 if rag_system else 503
    return jsonify(health_status), status_code


@app.route('/api/query', methods=['POST'])
@jwt_required()
def query():
    """Query the knowledge base"""
    global rag_system

    try:
        if not rag_system:
            return jsonify({'error': 'RAG system not initialized'}), 503

        data = request.get_json()
        query_text = data.get('query', '')
        k = data.get('k', 5)

        if not query_text:
            return jsonify({'error': 'Query is required'}), 400

        # Query the RAG system
        results = rag_system.query(query_text, k)

        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'score': result['score'],
                'content': result['document']['content'],
                'source': result['document']['source'],
                'chunk_id': result['document']['chunk_id']
            })

        response = {
            'query': query_text,
            'results': formatted_results,
            'count': len(formatted_results),
            'top_score': formatted_results[0]['score'] if formatted_results else 0
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ingest', methods=['POST'])
@jwt_required()
def ingest():
    """Ingest documents"""
    global rag_system, documents_count, embeddings_count

    try:
        files = request.files.getlist('files')

        if not files:
            return jsonify({'error': 'No files provided'}), 400

        # Get data path
        data_path = os.getenv('DATA_PATH', './data/documents')

        # Ensure data directory exists
        os.makedirs(data_path, exist_ok=True)

        ingested_count = 0
        for file in files:
            if file.filename and file.filename.endswith('.txt'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(data_path, filename)

                # Save file
                file.save(filepath)
                ingested_count += 1
                logger.info(f"Ingested file: {filename}")

        if ingested_count > 0:
            # Reinitialize RAG system with new documents
            logger.info("Reinitializing RAG system with new documents...")
            init_success = initialize_rag_system()

            if not init_success:
                return jsonify({
                    'error': 'Failed to process ingested documents',
                    'files_ingested': ingested_count
                }), 500

        return jsonify({
            'message': f'Successfully ingested {ingested_count} files',
            'files_ingested': ingested_count,
            'documents_indexed': documents_count,
            'embeddings_created': embeddings_count
        }), 200
    except Exception as e:
        logger.error(f"Error ingesting files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
@jwt_required()
def status():
    """Get system status"""
    global rag_system, documents_count, embeddings_count

    system_status = {
        'status': 'operational' if rag_system else 'initialization_failed',
        'documents_indexed': documents_count,
        'embeddings_stored': embeddings_count,
        'api_key_configured': bool(os.getenv('OPENAI_API_KEY')),
        'data_path': os.getenv('DATA_PATH', './data/documents'),
        'chunk_size': int(os.getenv('CHUNK_SIZE', 1000)),
        'overlap': int(os.getenv('OVERLAP', 200))
    }

    return jsonify(system_status), 200


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
