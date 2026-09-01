import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-task-manager-123")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Configurações de Email / Notificações
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER", "taskmanager@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "dev_email_pass")

    # Constantes do Domínio
    VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
    VALID_ROLES = ['user', 'admin', 'manager']
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

settings = Settings()
