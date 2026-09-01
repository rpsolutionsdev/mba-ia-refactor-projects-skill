# Heurísticas de Análise de Projetos

Este documento fornece as diretrizes e heurísticas para a **Fase 1 (Análise do Projeto)** da skill `/refactor-arch`.

---

## 1. Identificação de Linguagem e Runtime

| Arquivo Indicador | Linguagem / Runtime | Heurística de Confirmação |
| :--- | :--- | :--- |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | **Python** | Verificar imports como `import`, `from ... import`, `def `, indentação por 4 espaços. |
| `package.json`, `package-lock.json`, `yarn.lock`, `*.js`, `*.ts` | **Node.js / TypeScript** | Verificar `require(...)`, `import ... from`, `module.exports`, `export default`. |
| `pom.xml`, `build.gradle`, `*.java` | **Java** | Verificar `package `, `public class `, anotações `@...`. |
| `go.mod`, `go.sum`, `*.go` | **Go** | Verificar `package main`, `func `, `import (...)`. |
| `composer.json`, `*.php` | **PHP** | Verificar `<?php`, `namespace `, `use `. |
| `Gemfile`, `*.rb` | **Ruby** | Verificar `gem '...'`, `class ... < ...`, `def ... end`. |

---

## 2. Identificação de Frameworks Web

### Python
* **Flask**: `import flask`, `from flask import Flask, jsonify, request, Blueprint`, `Flask(__name__)`, `@app.route`, `Blueprint(...)`.
* **FastAPI**: `from fastapi import FastAPI, APIRouter`, `FastAPI()`, `@app.get`, `@app.post`.
* **Django**: `django`, `settings.py`, `urls.py`, `manage.py`, `models.Model`, `views.py`.

### Node.js
* **Express**: `require('express')`, `import express from 'express'`, `express()`, `app.use()`, `app.get()`, `app.post()`, `router.get()`.
* **NestJS**: `@nestjs/core`, `@Controller()`, `@Injectable()`, `@Module()`.
* **Fastify**: `require('fastify')`, `fastify()`, `fastify.register()`.

---

## 3. Identificação de Banco de Dados e Persistência

| Padrão / Driver | Tecnologia | Características Encontradas |
| :--- | :--- | :--- |
| `sqlite3`, `sqlite:///`, `:memory:`, `.db` | **SQLite** | `sqlite3.connect()`, `new sqlite3.Database()`, DDL inline. |
| `psycopg2`, `pg`, `postgres://` | **PostgreSQL** | Queries relacionais, conexões pooling. |
| `mysql`, `mysql2`, `pymysql` | **MySQL / MariaDB** | Queries SQL padrão. |
| `sqlalchemy`, `flask_sqlalchemy` | **SQLAlchemy ORM** | `db.Model`, `db.Column`, `query.filter_by()`. |
| `prisma`, `prisma.schema` | **Prisma ORM** | Modelos declarativos, `prisma.<model>.findMany()`. |
| `mongoose`, `mongodb` | **MongoDB (NoSQL)** | `mongoose.Schema()`, `db.collection()`. |

---

## 4. Mapeamento do Domínio de Negócio

Para identificar o domínio da aplicação:
1. Examine os nomes das rotas/endpoints (`/produtos`, `/usuarios`, `/pedidos`, `/checkout`, `/tasks`, `/reports`).
2. Examine as entidades e tabelas (`users`, `products`, `orders`, `tasks`, `courses`, `enrollments`, `payments`).
3. Formule um resumo conciso do domínio (Ex: *E-commerce API com catálogo de produtos, gestão de usuários e processamento de pedidos* ou *LMS API com catálogo de cursos e fluxo de checkout e matrículas*).

---

## 5. Mapeamento da Arquitetura Atual

Classifique a arquitetura atual em uma das categorias:
* **Monolítica Não-Estruturada (God Files)**: Todo o código (rotas, queries SQL, lógica de negócio, views) concentrado em 1 a 4 arquivos grandes sem separação de responsabilidades.
* **Semi-Estruturada**: Existe divisão em pastas (ex: `models/`, `routes/`), mas as camadas estão altamente acopladas, com regras de negócio vazando para as rotas ou models.
* **MVC Parcial / Desbalanceado**: Camadas MVC existem formalmente, mas os controllers ou models acumulam responsabilidades indevidas (Fat Controllers / Fat Models).
