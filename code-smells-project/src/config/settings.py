import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-change-in-prod")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    DB_PATH = os.getenv("DB_PATH", "loja.db")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-secret-token-123")

    # Regras de Negócio / Constantes
    DISCOUNT_TIER_1_THRESHOLD = 10000.0
    DISCOUNT_TIER_1_RATE = 0.10
    DISCOUNT_TIER_2_THRESHOLD = 5000.0
    DISCOUNT_TIER_2_RATE = 0.05
    DISCOUNT_TIER_3_THRESHOLD = 1000.0
    DISCOUNT_TIER_3_RATE = 0.02

    VALID_PRODUCT_CATEGORIES = [
        "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"
    ]
    VALID_ORDER_STATUSES = [
        "pendente", "aprovado", "enviado", "entregue", "cancelado"
    ]

settings = Settings()
