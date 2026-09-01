from flask import Blueprint
from src.controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__)

produto_bp.add_url_rule("/produtos", "listar_produtos", ProdutoController.listar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/busca", "buscar_produtos", ProdutoController.buscar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/<int:produto_id>", "buscar_produto", ProdutoController.buscar_produto, methods=["GET"])
produto_bp.add_url_rule("/produtos", "criar_produto", ProdutoController.criar_produto, methods=["POST"])
produto_bp.add_url_rule("/produtos/<int:produto_id>", "atualizar_produto", ProdutoController.atualizar_produto, methods=["PUT"])
produto_bp.add_url_rule("/produtos/<int:produto_id>", "deletar_produto", ProdutoController.deletar_produto, methods=["DELETE"])
