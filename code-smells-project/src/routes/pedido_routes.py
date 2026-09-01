from flask import Blueprint
from src.controllers.pedido_controller import PedidoController

pedido_bp = Blueprint("pedidos", __name__)

pedido_bp.add_url_rule("/pedidos", "criar_pedido", PedidoController.criar_pedido, methods=["POST"])
pedido_bp.add_url_rule("/pedidos", "listar_todos_pedidos", PedidoController.listar_todos_pedidos, methods=["GET"])
pedido_bp.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", PedidoController.listar_pedidos_usuario, methods=["GET"])
pedido_bp.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", PedidoController.atualizar_status_pedido, methods=["PUT"])
