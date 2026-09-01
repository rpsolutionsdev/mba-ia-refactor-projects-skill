from flask import Blueprint
from src.controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', 'get_users', UserController.get_users, methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', 'get_user', UserController.get_user, methods=['GET'])
user_bp.add_url_rule('/users', 'create_user', UserController.create_user, methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', 'update_user', UserController.update_user, methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', 'delete_user', UserController.delete_user, methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', 'get_user_tasks', UserController.get_user_tasks, methods=['GET'])
user_bp.add_url_rule('/login', 'login', UserController.login, methods=['POST'])
