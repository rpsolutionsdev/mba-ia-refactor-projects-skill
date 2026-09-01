"""
Entrypoint principal da Task Manager API refatorada para o padrão MVC.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app
from src.config.settings import settings

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("TASK MANAGER API INICIADA (ARQUITETURA MVC)")
    print(f"Rodando em http://{settings.HOST}:{settings.PORT}")
    print("=" * 50)
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
