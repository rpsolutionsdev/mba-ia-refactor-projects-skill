from flask import Blueprint
from src.controllers.task_controller import TaskController

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', 'get_tasks', TaskController.get_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/search', 'search_tasks', TaskController.search_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', 'task_stats', TaskController.task_stats, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'get_task', TaskController.get_task, methods=['GET'])
task_bp.add_url_rule('/tasks', 'create_task', TaskController.create_task, methods=['POST'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'update_task', TaskController.update_task, methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'delete_task', TaskController.delete_task, methods=['DELETE'])
