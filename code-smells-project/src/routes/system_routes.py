from flask import Blueprint
from src.controllers.system_controller import SystemController

system_bp = Blueprint("system", __name__)

system_bp.add_url_rule("/", "index", SystemController.index, methods=["GET"])
system_bp.add_url_rule("/health", "health_check", SystemController.health_check, methods=["GET"])
system_bp.add_url_rule("/admin/reset-db", "reset_database", SystemController.reset_database, methods=["POST"])
system_bp.add_url_rule("/admin/query", "executar_query", SystemController.executar_query, methods=["POST"])
