from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from src.config.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamento com tarefas
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        # NUNCA expor a hash da senha no retorno público
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        # Validação estrita com PBKDF2/scrypt - rejeita qualquer algoritmo fraco ou obsoleto
        if self.password and (self.password.startswith("pbkdf2:") or self.password.startswith("scrypt:")):
            return check_password_hash(self.password, pwd)
        return False

    def is_admin(self):
        return self.role == 'admin'
