# Guia de Deploy e Plano de Notificações de Negócio

Você fez excelentes perguntas! O deploy em produção e a separação de responsabilidades para alertas são cruciais para um sistema robusto. Abaixo detalho como você subirá isso para a nuvem e como implementaremos os novos alertas.

---

## Parte 1: Como fazer o Deploy em Produção?

O código atual foi arquitetado para ser independente de nuvem (agnóstico). Você pode subir na AWS, DigitalOcean, Hetzner, etc. O processo recomendado é usar uma **VPS (Virtual Private Server)** com Ubuntu:

1. **Servidor:** Você aluga uma VPS básica (ex: DigitalOcean Droplet por $5/mês).
2. **Instalação:** Instala apenas o Docker e o Docker Compose no servidor.
3. **Código e Variáveis:** 
   - Você faz um `git clone` do seu repositório lá dentro.
   - Cria o arquivo `.env` com senhas reais e seguras (senhas fortes para o Postgres, chave JWT segura, etc).
4. **Subindo:** Roda `docker compose up --build -d`.
5. **Proxy Reverso:** (Opcional, mas recomendado) Configura um Nginx ou Caddy Server na frente da porta 8000 para habilitar SSL (HTTPS) automático.

*(Futuramente, podemos automatizar isso usando o GitHub Actions, para que um `git push` atualize o servidor automaticamente).*

---

## Parte 2: Arquitetura para Múltiplos Webhooks

O webhook que criamos (o `DiscordWebhookHandler`) é para **Erros de Sistema** (ex: banco caiu, erro de código 500). Isso pertence à camada de *Infraestrutura/Logs*.

Se você quer alertas para **Eventos de Negócio** (ex: "Novo Usuário Cadastrado", "E-mail Enviado"), isso NÃO deve ser logado como erro. Precisamos criar um serviço na camada de Negócio.

### Proposta de Implementação (Clean Architecture)

Vamos criar um `NotificationService` que enviará mensagens formatadas para webhooks separados.

#### 1. Novas Variáveis de Ambiente (`config.py`)
Vamos separar as URLs para você ter canais diferentes no seu Discord:
- `discord_webhook_errors`: Canal #alertas-sistema
- `discord_webhook_users`: Canal #novos-clientes
- `discord_webhook_emails`: Canal #auditoria-emails

#### 2. Criação do Contrato e Serviço
- **[NEW]** `src/app/core/contracts/notification.py`: Definirá a interface `NotificationContract` com métodos como `notify_new_user(user_name)` e `notify_email_sent(email_to)`.
- **[NEW]** `src/app/infrastructure/notifications/discord_notifier.py`: Implementação do contrato que fará o disparo assíncrono (HTTP) para as URLs correspondentes.

#### 3. Injeção nos Casos de Uso
- No **Cadastro de Usuário** (`UserRegisterUseCase`), injetaremos o serviço e, após salvar no banco, chamaremos: `await self.notifier.notify_new_user(user.name)`.
- No **Worker de E-mail** (`emails/worker.py`), ao confirmar o envio com sucesso no provedor SMTP, chamaremos: `await self.notifier.notify_email_sent(msg.to)`.

---

> [!IMPORTANT]
> **Questões Abertas para Você:**
> 
> 1. Você concorda com essa separação (um Webhook para "Erros", outro para "Usuários" e outro para "E-mails")? 
> 2. Podemos iniciar a escrita do código desse `NotificationService` injetável agora mesmo?
