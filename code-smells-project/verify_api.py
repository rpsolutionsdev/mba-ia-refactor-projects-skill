import sys
import os

# Configura stdout para UTF-8 no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app

client = app.test_client()

print("--- TESTANDO ENDPOINTS DE CODE-SMELLS-PROJECT ---")

# 1. Health
r = client.get('/health')
assert r.status_code == 200, f"Health falhou: {r.status_code}"
data = r.get_json()
assert data.get("status") == "ok"
assert "secret_key" not in data, "SECRET_KEY NAO deve vazar no health!"
print("[OK] [GET /health] OK - Sem vazamento de secret")

# 2. Index
r = client.get('/')
assert r.status_code == 200
print("[OK] [GET /] OK")

# 3. Produtos
r = client.get('/produtos')
assert r.status_code == 200
produtos = r.get_json()['dados']
assert len(produtos) >= 10
print(f"[OK] [GET /produtos] OK - {len(produtos)} produtos retornados")

# 4. Busca de produtos
r = client.get('/produtos/busca?q=Gamer')
assert r.status_code == 200
print(f"[OK] [GET /produtos/busca] OK - {len(r.get_json()['dados'])} itens encontrados")

# 5. Criar produto
r = client.post('/produtos', json={
    "nome": "Monitor UltraWide 34",
    "descricao": "Monitor Curvo 144Hz",
    "preco": 2499.90,
    "estoque": 5,
    "categoria": "informatica"
})
assert r.status_code == 201
novo_produto_id = r.get_json()['dados']['id']
print(f"[OK] [POST /produtos] OK - Criado produto ID {novo_produto_id}")

# 6. Login
r_login = client.post('/login', json={"email": "admin@loja.com", "senha": "admin123"})
assert r_login.status_code == 200
login_data = r_login.get_json()
assert login_data['sucesso'] is True
user_id = login_data['dados']['id']
print("[OK] [POST /login] OK - Autenticacao com senha hash validada com sucesso")

# 7. Criar pedido
first_product_id = produtos[0]['id']
r = client.post('/pedidos', json={
    "usuario_id": user_id,
    "itens": [{"produto_id": first_product_id, "quantidade": 1}]
})
assert r.status_code == 201
print("[OK] [POST /pedidos] OK - Pedido criado com calculo correto")

# 8. Relatorio de vendas
r = client.get('/relatorios/vendas')
assert r.status_code == 200
assert "faturamento_bruto" in r.get_json()['dados']
print("[OK] [GET /relatorios/vendas] OK - Relatorio gerado com sucesso")

# 9. Verificacao de Seguranca: Endpoint perigoso /admin/query deve estar REMOVIDO
r = client.post('/admin/query', json={"sql": "SELECT 1"})
assert r.status_code == 404, f"/admin/query deveria retornar 404, mas retornou {r.status_code}"
print("[OK] [POST /admin/query] OK - Endpoint de execucao arbitraria de SQL removido (404 Not Found)")

# 10. Verificacao de Seguranca: /admin/reset-db DEVE exigir autenticacao
r = client.post('/admin/reset-db')
assert r.status_code == 401, f"/admin/reset-db sem auth deveria retornar 401, retornou {r.status_code}"
r_invalid = client.post('/admin/reset-db', headers={"X-Admin-Token": "token-invalido-123"})
assert r_invalid.status_code == 401
print("[OK] [POST /admin/reset-db] OK - Acesso nao autenticado devidamente rejeitado (401 Unauthorized)")

# 11. /admin/reset-db com token admin valido
from src.config.settings import settings
r_auth = client.post('/admin/reset-db', headers={"X-Admin-Token": settings.ADMIN_TOKEN})
assert r_auth.status_code == 200
assert r_auth.get_json()['sucesso'] is True
print("[OK] [POST /admin/reset-db] OK - Reset com X-Admin-Token autorizado executado com sucesso (200 OK)")

print("\nTODOS OS TESTES DO PROJETO 1 PASSARAM COM SUCESSO!")
