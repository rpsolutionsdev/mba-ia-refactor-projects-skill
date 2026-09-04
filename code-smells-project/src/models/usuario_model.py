from werkzeug.security import generate_password_hash, check_password_hash
from src.config.database import get_connection

class UsuarioModel:
    @staticmethod
    def get_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_por_id(usuario_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_por_email(email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha, tipo, criado_em FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def criar(nome, email, senha, tipo="cliente"):
        conn = get_connection()
        cursor = conn.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    @staticmethod
    def autenticar(email, senha):
        usuario = UsuarioModel.get_por_email(email)
        if not usuario:
            return None
        
        # Validação estrita de hash criptográfico sem fallback para texto puro ou cifras fracas
        hash_armazenado = usuario.get("senha", "")
        senha_valida = False
        if hash_armazenado and (hash_armazenado.startswith("pbkdf2:") or hash_armazenado.startswith("scrypt:")):
            senha_valida = check_password_hash(hash_armazenado, senha)
        else:
            senha_valida = False

        if senha_valida:
            return {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "tipo": usuario["tipo"]
            }
        return None
