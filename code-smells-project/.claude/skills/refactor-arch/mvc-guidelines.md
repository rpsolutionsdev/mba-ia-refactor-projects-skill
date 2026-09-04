# Diretrizes Arquiteturais para o Padrão MVC Alvo

Este documento estabelece as regras e padrões para a organização em camadas MVC aplicada na **Fase 3 (Refatoração)** da skill `/refactor-arch`.

---

## 🏛️ Estrutura Padrão de Diretórios

Toda aplicação refatorada deve seguir uma estrutura limpa e desacoplada, tipicamente sob `src/`:

```
src/
├── config/             # Configurações de ambiente, conexões e constantes
│   ├── database.*      # Conexão e inicialização com o banco de dados
│   └── settings.*      # Variáveis de ambiente (SECRET_KEY, portas, etc.)
│
├── models/             # Camada de Dados (M)
│   ├── <entidade>_model.*
│   └── ...
│
├── views/ (ou routes/) # Camada de Visualização / Roteamento (V)
│   ├── <dominio>_routes.*
│   └── ...
│
├── controllers/        # Camada de Controle (C)
│   ├── <dominio>_controller.*
│   └── ...
│
├── services/           # Regras de Negócio e Serviços Especializados (Opcional/Recomendado)
│   ├── <dominio>_service.*
│   └── ...
│
├── middlewares/        # Interceptadores (Auth, Error Handling, Validação)
│   └── error_handler.*
│
└── app.*               # Composition Root / Ponto de entrada limpo
```

---

## 📐 Responsabilidades de Cada Camada

### 1. `config/` (Configurações)
* **Responsabilidade**: Centralizar credenciais, carregamento de variáveis de ambiente (`.env`), constantes globais do sistema e pools/conexões de banco de dados.
* **Regra**: **Zero secrets hardcoded**. Nenhuma credencial de produção pode estar fixada no código.

### 2. `models/` (Modelos de Dados)
* **Responsabilidade**: Abstrair o acesso a dados, schemas de tabelas, entidades e queries de persistência.
* **Regra**: Todas as queries SQL devem utilizar **parâmetros vinculados (prepared statements)**. É proibido concatenar strings diretamente em queries. Models não devem manipular objetos de requisição HTTP (`request`, `req`, `res`).

### 3. `views/` / `routes/` (Roteamento e Apresentação)
* **Responsabilidade**: Declarar endpoints HTTP (URLs, métodos `GET`, `POST`, `PUT`, `DELETE`), vincular rotas aos métodos correspondentes dos Controllers e serializar a resposta.
* **Regra**: Não conter lógica de negócio, nem queries de banco de dados. Devem ser finas (*Thin Routes*).

### 4. `controllers/` (Controladores)
* **Responsabilidade**: Receber os dados da requisição HTTP (parâmetros, body, headers), orquestrar as chamadas aos Models/Services correspondentes e retornar respostas com códigos de status HTTP semânticos (200, 201, 400, 404, 500).
* **Regra**: Manter os controllers focados em orquestração, sem executar SQL direto.

### 5. `services/` (Serviços de Domínio)
* **Responsabilidade**: Encapsular lógicas de negócio complexas, cálculos, validações de domínio e integrações externas (gateways de pagamento, envio de emails/notificações).
* **Regra**: Não devem depender de objetos de requisição HTTP (`req`, `res`), permitindo testes unitários fáceis.

### 6. `middlewares/` (Tratamento de Erros e Filtros)
* **Responsabilidade**: Captura global de exceções, formatação padronizada de mensagens de erro JSON, logging centralizado e validações transversais.
* **Regra**: Nunca vazar stack traces detalhados para o cliente em ambiente de produção.

### 7. `app.*` (Composition Root)
* **Responsabilidade**: Ponto de entrada da aplicação. Instancia o servidor web, aplica middlewares globais, registra as rotas/blueprints e inicializa a escuta de portas.
* **Regra**: Conter menos de 50 linhas, atuando apenas como orquestrador de inicialização.

### 8. Limpeza Arquitetural & Não-Coexistência de Código Legado
* **Responsabilidade**: Extirpar completamente os artefatos legados após a migração para a nova arquitetura MVC em `src/`.
* **Regra**: Todo arquivo ou diretório legado que foi decomposto ou substituído (God Classes como `AppManager.js`, scripts na raiz como `models.py`, `controllers.py`, `database.py`, utilitários vulneráveis como `utils.js`, ou diretórios legados `models/`, `routes/`, `services/`) **deve ser fisicamente removido do repositório**. É terminantemente proibido deixar arquivos legados coexistindo em paralelo com a pasta `src/`. As vulnerabilidades auditadas na Fase 2 devem deixar de existir em qualquer arquivo do projeto.

### 9. Criptografia Estrita & Proibição Absoluta de Fallbacks Inseguros
* **Responsabilidade**: Garantir proteção inviolável de credenciais e dados sensíveis.
* **Regra**: O armazenamento e validação de senhas devem utilizar exclusivamente algoritmos criptográficos robustos de derivação de chave com salt único (PBKDF2, scrypt, Argon2, bcrypt). **É terminantemente proibido implementar ou manter caminhos alternativos (fallbacks) para algoritmos inseguros ou obsoletos** (como `hashlib.md5(...)`, `sha1` sem salt, ou validações `|| plainPassword === hashedPassword`). Se a senha armazenada for inválida ou estiver em formato inseguro, a autenticação DEVE falhar imediatamente.
