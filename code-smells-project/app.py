"""
Entrypoint principal da aplicação refatorada para o padrão MVC.
Delega a inicialização para a fábrica de aplicação em src.app.
"""
import sys
import os

# Garante inclusão do diretório raiz no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app
from src.config.settings import settings

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO (ARQUITETURA MVC)")
    print(f"Rodando em http://{settings.HOST}:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
