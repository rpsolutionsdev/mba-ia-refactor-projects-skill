from src.config.database import get_connection

class PedidoModel:
    @staticmethod
    def criar(usuario_id, itens):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            total = 0.0
            produtos_validados = []

            for item in itens:
                produto_id = item.get("produto_id")
                qtd = item.get("quantidade", 0)

                cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,))
                prod = cursor.fetchone()
                if not prod:
                    conn.close()
                    return {"erro": f"Produto {produto_id} não encontrado"}
                if prod["estoque"] < qtd:
                    conn.close()
                    return {"erro": f"Estoque insuficiente para {prod['nome']}"}

                preco_unit = float(prod["preco"])
                total += preco_unit * qtd
                produtos_validados.append({
                    "produto_id": produto_id,
                    "quantidade": qtd,
                    "preco_unitario": preco_unit
                })

            cursor.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total)
            )
            pedido_id = cursor.lastrowid

            for item in produtos_validados:
                cursor.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
                )
                cursor.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                    (item["quantidade"], item["produto_id"])
                )

            conn.commit()
            conn.close()
            return {"pedido_id": pedido_id, "total": total}

        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_pedidos(usuario_id=None):
        conn = get_connection()
        cursor = conn.cursor()

        if usuario_id is not None:
            cursor.execute("SELECT id, usuario_id, status, total, criado_em FROM pedidos WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,))
        else:
            cursor.execute("SELECT id, usuario_id, status, total, criado_em FROM pedidos ORDER BY id DESC")
        
        pedidos_rows = cursor.fetchall()
        if not pedidos_rows:
            conn.close()
            return []

        pedido_ids = [p["id"] for p in pedidos_rows]
        placeholders = ",".join("?" * len(pedido_ids))

        # Busca otimizada de todos os itens com JOIN no produto (evita N+1)
        query_itens = f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome as produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.pedido_id IN ({placeholders})
        """
        cursor.execute(query_itens, tuple(pedido_ids))
        itens_rows = cursor.fetchall()
        conn.close()

        itens_por_pedido = {}
        for item in itens_rows:
            pid = item["pedido_id"]
            if pid not in itens_por_pedido:
                itens_por_pedido[pid] = []
            itens_por_pedido[pid].append({
                "produto_id": item["produto_id"],
                "produto_nome": item["produto_nome"] or "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"]
            })

        resultado = []
        for p in pedidos_rows:
            resultado.append({
                "id": p["id"],
                "usuario_id": p["usuario_id"],
                "status": p["status"],
                "total": p["total"],
                "criado_em": p["criado_em"],
                "itens": itens_por_pedido.get(p["id"], [])
            })

        return resultado

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        conn.commit()
        alterados = cursor.rowcount
        conn.close()
        return alterados > 0
