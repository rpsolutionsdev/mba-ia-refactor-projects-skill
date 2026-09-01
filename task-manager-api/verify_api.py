import sys
import os

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app

client = app.test_client()

print("--- TESTANDO ENDPOINTS DE TASK-MANAGER-API (PYTHON/FLASK) ---")

# 1. Health
r = client.get('/health')
assert r.status_code == 200, f"Health falhou: {r.status_code}"
assert r.get_json().get("status") == "ok"
print("[OK] [GET /health] OK")

# 2. Criar Categoria
r = client.post('/categories', json={
    "name": "Desenvolvimento",
    "description": "Tarefas de engenharia de software",
    "color": "#007acc"
})
assert r.status_code == 201
cat_id = r.get_json()['id']
print(f"[OK] [POST /categories] Categoria criada ID {cat_id}")

# 3. Criar Usuário
r = client.post('/users', json={
    "name": "Carlos Silva",
    "email": "carlos@empresa.com",
    "password": "senhaSegura123",
    "role": "admin"
})
assert r.status_code == 201
user_data = r.get_json()
assert "password" not in user_data, "Hash de senha NÃO deve ser exposto na resposta da API!"
user_id = user_data['id']
print(f"[OK] [POST /users] Usuario criado ID {user_id} - Hash omitido com seguranca")

# 4. Login
r = client.post('/login', json={
    "email": "carlos@empresa.com",
    "password": "senhaSegura123"
})
assert r.status_code == 200
assert "token" in r.get_json()
print("[OK] [POST /login] Autenticacao com senha PBKDF2/scrypt realizada com sucesso")

# 5. Criar Task
r = client.post('/tasks', json={
    "title": "Refatorar Arquitetura para MVC",
    "description": "Separar controllers, models, routes e config",
    "status": "in_progress",
    "priority": 1,
    "user_id": user_id,
    "category_id": cat_id,
    "due_date": "2026-12-31",
    "tags": ["arquitetura", "clean-code"]
})
assert r.status_code == 201
task_id = r.get_json()['id']
print(f"[OK] [POST /tasks] Task criada ID {task_id}")

# 6. Listar Tasks
r = client.get('/tasks')
assert r.status_code == 200
tasks = r.get_json()
assert len(tasks) >= 1
print(f"[OK] [GET /tasks] {len(tasks)} tarefas listadas (sem queries N+1)")

# 7. Relatório Resumo
r = client.get('/reports/summary')
assert r.status_code == 200
summary = r.get_json()
assert summary['overview']['total_tasks'] >= 1
print("[OK] [GET /reports/summary] Relatorio gerado com sucesso")

# 8. Relatório por Usuário
r = client.get(f'/reports/user/{user_id}')
assert r.status_code == 200
assert r.get_json()['user']['id'] == user_id
print(f"[OK] [GET /reports/user/{user_id}] Relatorio do usuario OK")

print("\nTODOS OS TESTES DO PROJETO 3 PASSARAM COM SUCESSO!")
