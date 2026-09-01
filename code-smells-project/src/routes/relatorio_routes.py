from flask import Blueprint
from src.controllers.relatorio_controller import RelatorioController

relatorio_bp = Blueprint("relatorios", __name__)

relatorio_bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", RelatorioController.relatorio_vendas, methods=["GET"])
