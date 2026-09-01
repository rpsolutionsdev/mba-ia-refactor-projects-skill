from src.config.database import get_connection

class ProdutoModel:
    @staticmethod
    def get_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, preco, estoque, categoria, ativo, criado_em FROM produtos")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_por_id(produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, preco, estoque, categoria, ativo, criado_em FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def criar(nome, descricao, preco, estoque, categoria):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    @staticmethod
    def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id)
        )
        conn.commit()
        alterados = cursor.rowcount
        conn.close()
        return alterados > 0

    @staticmethod
    def deletar(produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        alterados = cursor.rowcount
        conn.close()
        return alterados > 0

    @staticmethod
    def buscar(termo="", categoria=None, preco_min=None, preco_max=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, nome, descricao, preco, estoque, categoria, ativo, criado_em FROM produtos WHERE 1=1"
        params = []

        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params.extend([f"%{termo}%", f"%{termo}%"])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
