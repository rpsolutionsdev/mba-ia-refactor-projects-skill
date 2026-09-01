from src.config.database import get_connection
from src.config.settings import settings

class RelatorioModel:
    @staticmethod
    def gerar_relatorio_vendas():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento_raw = cursor.fetchone()[0]
        faturamento = float(faturamento_raw) if faturamento_raw is not None else 0.0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]
        conn.close()

        # Cálculo de desconto usando constantes
        desconto = 0.0
        if faturamento > settings.DISCOUNT_TIER_1_THRESHOLD:
            desconto = faturamento * settings.DISCOUNT_TIER_1_RATE
        elif faturamento > settings.DISCOUNT_TIER_2_THRESHOLD:
            desconto = faturamento * settings.DISCOUNT_TIER_2_RATE
        elif faturamento > settings.DISCOUNT_TIER_3_THRESHOLD:
            desconto = faturamento * settings.DISCOUNT_TIER_3_RATE

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
        }
