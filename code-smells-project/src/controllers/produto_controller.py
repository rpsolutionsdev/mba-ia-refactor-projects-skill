import logging
from flask import request, jsonify
from src.models.produto_model import ProdutoModel
from src.config.settings import settings

logger = logging.getLogger(__name__)

class ProdutoController:
    @staticmethod
    def listar_produtos():
        produtos = ProdutoModel.get_todos()
        logger.info(f"Listando {len(produtos)} produtos")
        return jsonify({"dados": produtos, "sucesso": True}), 200

    @staticmethod
    def buscar_produto(produto_id):
        produto = ProdutoModel.get_por_id(produto_id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404

    @staticmethod
    def buscar_produtos():
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        try:
            if preco_min is not None:
                preco_min = float(preco_min)
            if preco_max is not None:
                preco_max = float(preco_max)
        except ValueError:
            return jsonify({"erro": "Preço mínimo ou máximo inválido"}), 400

        resultados = ProdutoModel.buscar(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

    @staticmethod
    def criar_produto():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        campos_obrigatorios = ["nome", "preco", "estoque"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"{campo.capitalize()} é obrigatório"}), 400

        nome = str(dados["nome"]).strip()
        descricao = str(dados.get("descricao", "")).strip()
        
        try:
            preco = float(dados["preco"])
            estoque = int(dados["estoque"])
        except (ValueError, TypeError):
            return jsonify({"erro": "Preço ou estoque com formato numérico inválido"}), 400

        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400
        if len(nome) < 2:
            return jsonify({"erro": "Nome muito curto"}), 400
        if len(nome) > 200:
            return jsonify({"erro": "Nome muito longo"}), 400
        if categoria not in settings.VALID_PRODUCT_CATEGORIES:
            return jsonify({"erro": f"Categoria inválida. Válidas: {settings.VALID_PRODUCT_CATEGORIES}"}), 400

        novo_id = ProdutoModel.criar(nome, descricao, preco, estoque, categoria)
        logger.info(f"Produto criado com ID: {novo_id}")
        return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    @staticmethod
    def atualizar_produto(produto_id):
        produto_existente = ProdutoModel.get_por_id(produto_id)
        if not produto_existente:
            return jsonify({"erro": "Produto não encontrado"}), 404

        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        campos_obrigatorios = ["nome", "preco", "estoque"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"{campo.capitalize()} é obrigatório"}), 400

        nome = str(dados["nome"]).strip()
        descricao = str(dados.get("descricao", "")).strip()
        
        try:
            preco = float(dados["preco"])
            estoque = int(dados["estoque"])
        except (ValueError, TypeError):
            return jsonify({"erro": "Preço ou estoque inválido"}), 400

        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400

        ProdutoModel.atualizar(produto_id, nome, descricao, preco, estoque, categoria)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    @staticmethod
    def deletar_produto(produto_id):
        produto = ProdutoModel.get_por_id(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        ProdutoModel.deletar(produto_id)
        logger.info(f"Produto {produto_id} deletado")
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
