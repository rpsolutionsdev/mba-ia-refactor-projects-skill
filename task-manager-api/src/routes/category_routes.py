from flask import Blueprint
from src.controllers.category_controller import CategoryController

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', 'get_categories', CategoryController.get_categories, methods=['GET'])
category_bp.add_url_rule('/categories', 'create_category', CategoryController.create_category, methods=['POST'])
category_bp.add_url_rule('/categories/<int:cat_id>', 'update_category', CategoryController.update_category, methods=['PUT'])
category_bp.add_url_rule('/categories/<int:cat_id>', 'delete_category', CategoryController.delete_category, methods=['DELETE'])
