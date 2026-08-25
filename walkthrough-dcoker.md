# Containerização & Migrações Concluídas! 🐳

A infraestrutura básica para rodar o **LerTarot** em produção (ou ambiente dockerizado) foi finalizada com sucesso! Todos os arquivos necessários foram gerados e configurados.

## 🛠️ O que foi feito?

### 1. Docker & Docker Compose
- **`Dockerfile` (Multi-stage)**: Criado com dois estágios para garantir uma imagem final leve e segura. O Poetry é usado no primeiro estágio para baixar as dependências, e apenas os binários/pacotes são copiados para a imagem final de execução.
- **`docker-compose.yml`**: Configurado com três serviços:
  - `db`: Um container PostgreSQL 16 com volume persistente (`postgres_data`).
  - `api`: O backend FastAPI (mapeado na porta `8000`), rodando através do Gunicorn/Uvicorn.
  - `worker`: O serviço de e-mail consumindo a mesma imagem do backend, mas sobrescrevendo o comando inicial para rodar o seu `cli.py` de forma independente.
- **`scripts/entrypoint.sh`**: Um script de inicialização inteligente para o container da API. Ele garante que as migrações do banco sejam aplicadas (`alembic upgrade head`) ANTES da API subir, evitando inconsistências.

### 2. Alembic (Migrations)
- A estrutura do Alembic foi inicializada com suporte nativo a chamadas assíncronas (`-t async`).
- O arquivo `alembic/env.py` foi fortemente customizado para importar seu `Base.metadata` e injetar a string de conexão nativamente a partir do `config.py`, respeitando assim suas variáveis de ambiente (`.env`).
- Em `src/app/db/session.py`, ativamos o **Connection Pooling** (`pool_size=10, max_overflow=20`), o que é mandatório quando uma aplicação FastAPI precisa gerenciar múltiplas conexões concorrentes a um container Postgres.

---

> [!WARNING]
> **Próximos Passos (Sua vez!)**
> O ambiente local onde estou executando parece não ter o Docker instalado no `PATH` do Windows PowerShell (`docker: O termo não é reconhecido...`). Sendo assim, não pude gerar a primeira *migration* automaticamente, pois o banco de dados precisava estar rodando.
> 
> **Assim que você subir este projeto num ambiente com Docker, execute os seguintes comandos no terminal do repositório:**
> 1. Inicie o banco de dados em segundo plano:
>    ```bash
>    docker compose up -d db
>    ```
> 2. Gere a migração inicial baseada nos seus Models do SQLAlchemy:
>    ```bash
>    poetry run alembic revision --autogenerate -m "Initial schema"
>    ```
> 3. Suba o restante da aplicação (API e Worker):
>    ```bash
>    docker compose up --build -d
>    ```

## 🔮 O que vem agora?

Como você pontuou, a próxima etapa natural é a **expansão dos domínios próprios do negócio**. As fundações técnicas (arquitetura, banco, fila e deploy) estão prontas! 
Podemos começar a desenhar a lógica de negócio dos **Catálogos de Tarólogos** ou o **Agendamento de Consultas**. O que você quer atacar primeiro?
