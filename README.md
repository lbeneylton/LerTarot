# LerTarot API

Backend da plataforma LerTarot — agendamento de leituras de tarot com tarólogos e clientes.

Stack: **FastAPI**, **SQLAlchemy 2**, **Alembic**, **PostgreSQL**, **Poetry**.

## Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- PostgreSQL (local ou via scripts em `.postgres_local/`)

## Configuração

1. Clone o repositório e entre na pasta do projeto.

2. Instale as dependências:

```bash
poetry install
```

3. Copie o arquivo de ambiente e ajuste os valores:

```bash
copy .env.example .env
```

4. Crie o banco e aplique as migrations:

```bash
poetry run alembic upgrade head
```

## Executar a API

```bash
poetry run uvicorn app.main:app --reload --app-dir src
```

Documentação interativa: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Health check: `GET /health`

## Endpoints principais

| Método | Rota        | Descrição              |
|--------|-------------|------------------------|
| GET    | `/health`   | Status da API          |
| POST   | `/users`    | Cadastro de usuário    |

### Exemplo — cadastro de cliente

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Maria\",\"email\":\"maria@email.com\",\"password\":\"senha1234\",\"user_type\":\"client\"}"
```

Tipos de usuário: `client`, `reader`, `admin`.

## Testes

```bash
poetry run pytest
```

## Estrutura do projeto

```
src/app/
  core/       # config, exceções, segurança, handlers
  db/         # sessão, unit of work, migrations
  users/      # models, schemas, repository, service, router
  main.py     # aplicação FastAPI
migrations/   # Alembic
tests/        # pytest
```

## Próximos passos

- Autenticação (`POST /auth/login`) com JWT
- Domínio de agendamentos, serviços e especialidades
- Integração com Asaas para pagamentos
