# Playbook de Refatoração Arquitetural

Este documento contém os padrões concretos de transformação com exemplos de código **Antes / Depois** para guiar a **Fase 3 (Refatoração)** da skill `/refactor-arch`.

---

## 🛠️ Padrão 1: Eliminação de SQL Injection (Queries Parametrizadas)

### ❌ Antes (Python / Vulnerável)
```python
# Concatenação insegura de parâmetros
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")"
)
```

### ✅ Depois (Python / Parametrizado)
```python
# Utilização de placeholders seguros (?)
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
    (nome, preco)
)
```

---

## 🛠️ Padrão 2: Extração de Secrets Hardcoded para Configuração de Ambiente

### ❌ Antes (Node.js / Hardcoded)
```javascript
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

### ✅ Depois (Node.js / Environment Driven)
```javascript
require('dotenv').config();

const config = {
    dbPass: process.env.DB_PASS || "development_password",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_default",
    port: parseInt(process.env.PORT, 10) || 3000
};

module.exports = config;
```

---

## 🛠️ Padrão 3: Decomposição de God Class / God File em Camadas MVC

### ❌ Antes (Monolito Acoplado)
```javascript
// AppManager.js faz tudo: DDL, rotas, lógica e SQL
class AppManager {
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            this.db.get("SELECT * FROM courses ...", (err, course) => {
                // lógica de checkout, hash de senha e retorno http misturados
            });
        });
    }
}
```

### ✅ Depois (MVC Modularizado)
```javascript
// src/routes/checkoutRoutes.js (Rota fina)
const express = require('express');
const router = express.Router();
const CheckoutController = require('../controllers/checkoutController');

router.post('/checkout', CheckoutController.processCheckout);
module.exports = router;

// src/controllers/checkoutController.js (Controlador orquestrador)
const CheckoutService = require('../services/checkoutService');

exports.processCheckout = async (req, res, next) => {
    try {
        const result = await CheckoutService.checkout(req.body);
        return res.status(200).json(result);
    } catch (err) {
        next(err);
    }
};
```

---

## 🛠️ Padrão 4: Eliminação de Callback Hell com Async/Await e Promises

### ❌ Antes (Callback Pyramid)
```javascript
db.get("SELECT * FROM users WHERE id = ?", [id], (err, user) => {
    if (err) return res.status(500).send("Erro");
    db.all("SELECT * FROM orders WHERE user_id = ?", [user.id], (err, orders) => {
        if (err) return res.status(500).send("Erro");
        db.get("SELECT * FROM payments WHERE order_id = ?", [orders[0].id], (err, payment) => {
            res.json({ user, orders, payment });
        });
    });
});
```

### ✅ Depois (Clean Async/Await com Helper Promisificado)
```javascript
// Helper de banco assíncrono
const db = {
    get: (sql, params) => new Promise((resolve, reject) => {
        dbInstance.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
    }),
    all: (sql, params) => new Promise((resolve, reject) => {
        dbInstance.all(sql, params, (err, rows) => err ? reject(err) : resolve(rows));
    })
};

// Handler limpo
async function getUserDetails(req, res, next) {
    try {
        const user = await db.get("SELECT * FROM users WHERE id = ?", [req.params.id]);
        if (!user) return res.status(404).json({ error: "User not found" });
        const orders = await db.all("SELECT * FROM orders WHERE user_id = ?", [user.id]);
        res.json({ user, orders });
    } catch (err) {
        next(err);
    }
}
```

---

## 🛠️ Padrão 5: Hashing Seguro de Senhas e Omissão em Respostas

### ❌ Antes (MD5 Fraco e Exposição de Senha na API)
```python
import hashlib

class User(db.Model):
    def set_password(self, pwd):
        self.password = hashlib.md5(pwd.encode()).hexdigest()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password  # VAZAMENTO CRÍTICO!
        }
```

### ✅ Depois (Hash Seguro com Salt e Proteção Estrita sem Fallbacks)
```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    def set_password(self, pwd):
        # Gera hash seguro com salt automático (PBKDF2/scrypt)
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        # Validação estrita: NUNCA manter caminho alternativo/fallback para MD5, SHA1 ou plaintext
        if self.password and (self.password.startswith("pbkdf2:") or self.password.startswith("scrypt:")):
            return check_password_hash(self.password, pwd)
        return False  # Rejeita imediatamente hashes inseguros ou formatos obsoletos

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active
            # NUNCA retornar a senha/hash no payload da API!
        }
```

> [!CRITICAL]
> **Proibição Absoluta de Caminho Alternativo para Hashes Inseguros**: É inaceitável manter retrocompatibilidade com MD5, SHA1 sem salt, base64 ou plaintext (ex: `return self.password == hashlib.md5(pwd).hexdigest()` ou `|| plainPassword === hashedPassword`). Se uma credencial no banco for insegura, a autenticação DEVE falhar.

---

## 🛠️ Padrão 6: Eliminação do Problema de Consulta N+1 (Agregação / JOIN)

### ❌ Antes (Queries em Loop)
```python
users = User.query.all()
for u in users:
    # Query disparada a cada iteração!
    tasks = Task.query.filter_by(user_id=u.id).all()
    # processa tarefas...
```

### ✅ Depois (JOIN Único ou Subquery Otimizada)
```python
# Utilização de JOIN agrupado com COUNT
results = db.session.query(
    User.id,
    User.name,
    func.count(Task.id).label('total_tasks')
).outerjoin(Task, User.id == Task.user_id).group_by(User.id).all()
```

---

## 🛠️ Padrão 7: Extração de Fat Routes para Controllers e Services

### ❌ Antes (Rota com Lógica Pesada de Relatórios)
```python
@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    # 90 linhas de contagens manuais, cálculos de porcentagem e loops
    ...
```

### ✅ Depois (Separação Limpa)
```python
# src/routes/report_routes.py
@report_bp.route('/reports/summary', methods=['GET'])
def get_summary_report():
    return ReportController.get_summary()

# src/controllers/report_controller.py
class ReportController:
    @staticmethod
    def get_summary():
        data = ReportService.generate_summary()
        return jsonify(data), 200
```

---

## 🛠️ Padrão 8: Substituição de APIs Deprecated e Tratamento de Exceções

### ❌ Antes (API Deprecated e Bare Except)
```python
from datetime import datetime

# datetime.utcnow() está deprecated no Python 3.12+
data = datetime.utcnow()

try:
    process_data()
except: # Bare except engole todos os erros
    return "error", 500
```

### ✅ Depois (API Moderna e Captura Específica de Exceções)
```python
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Timestamp moderno e ciente de timezone
data = datetime.now(timezone.utc)

try:
    process_data()
except ValueError as e:
    logger.warning(f"Validation error: {e}")
    return jsonify({"error": str(e)}), 400
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500
```

---

## 🛠️ Padrão 9: Remoção Obrigatória e Purga de Código Legado Substituído

### ❌ Antes (Coexistência Indevida de Código Legado e Refatorado)
```
projeto/
├── app.py                      # Delegando para src/
├── models.py                   # Legado com SQL Injection e MD5 ainda vivo no repositório!
├── controllers.py              # Legado com segredos hardcoded ainda presente!
├── database.py                 # Conexão legada obsoleta
├── AppManager.js               # God Class com console.log de cartão de crédito ativo
├── src/
│   ├── utils.js                # Arquivo legado com pk_live_ e badCrypto não deletado!
│   ├── config/
│   ├── models/
│   └── controllers/
```
*Impacto Crítico*: Os apontamentos `CRITICAL` e `HIGH` identificados na auditoria (Fase 2) continuam existindo fisicamente no repositório nas linhas e arquivos originais, expondo segredos e código vulnerável.

### ✅ Depois (Repositório Limpo com Exclusão dos Arquivos Substituídos)
```
projeto/
├── app.py                      # Ponto de entrada / Composition Root limpo (<50 linhas)
└── src/                        # 100% da lógica e persistência concentrada aqui
    ├── config/                 # Configurações limpas via variáveis de ambiente
    ├── models/                 # Modelos seguros e parametrizados
    ├── routes/                 # Rotas desacopladas
    ├── controllers/            # Controllers orquestradores
    ├── services/               # Regras de negócio isoladas
    └── middlewares/            # Tratamento centralizado de erros
```

*Regras Mandatórias de Execução*:
1. **Deleção Física Obrigatória**: Todo arquivo ou diretório que foi substituído pela nova estrutura em `src/` (ex: `AppManager.js`, `src/utils.js`, `models.py`, `controllers.py`, `database.py` antigo, pastas legadas `models/`, `routes/`, `services/`) **DEVE ser permanentemente deletado**.
2. **Auditoria de Resíduos**: Após a Fase 3, verificar explicitamente se os arquivos e números de linha citados no relatório da Fase 2 deixaram de existir. Não pode haver duplicidade ou arquivos fantasmas no repositório.
3. **Entrypoints Limpos**: Somente manter arquivos na raiz que atuem como entrypoints delegando para `src/` (como `app.py` ou `package.json`).

