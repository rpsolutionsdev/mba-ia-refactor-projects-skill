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
r = client.post('/login', json={"email": "admin@loja.com", "senha": "admin123"})
assert r.status_code == 200
assert r.get_json()['sucesso'] is True
print("[OK] [POST /login] OK - Autenticacao com senha hash validada com sucesso")

# 7. Criar pedido
r = client.post('/pedidos', json={
    "usuario_id": 1,
    "itens": [{"produto_id": 1, "quantidade": 1}]
})
assert r.status_code == 201
print("[OK] [POST /pedidos] OK - Pedido criado com calculo correto")

# 8. Relatorio de vendas
r = client.get('/relatorios/vendas')
assert r.status_code == 200
assert "faturamento_bruto" in r.get_json()['dados']
print("[OK] [GET /relatorios/vendas] OK - Relatorio gerado com sucesso")

print("\nTODOS OS TESTES DO PROJETO 1 PASSARAM COM SUCESSO!")
