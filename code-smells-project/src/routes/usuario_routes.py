from flask import Blueprint
from src.controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.add_url_rule("/usuarios", "listar_usuarios", UsuarioController.listar_usuarios, methods=["GET"])
usuario_bp.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", UsuarioController.buscar_usuario, methods=["GET"])
usuario_bp.add_url_rule("/usuarios", "criar_usuario", UsuarioController.criar_usuario, methods=["POST"])
usuario_bp.add_url_rule("/login", "login", UsuarioController.login, methods=["POST"])
