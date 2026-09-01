from datetime import datetime, timezone
from flask import Blueprint, jsonify

system_bp = Blueprint('system', __name__)

@system_bp.route('/')
def index():
    return jsonify({'message': 'Task Manager API', 'version': '1.0'}), 200

@system_bp.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': str(datetime.now(timezone.utc))
    }), 200
