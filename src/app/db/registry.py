"""Registro de modelos SQLAlchemy para o Alembic."""

from app.modules.users.models import User, Client, Reader
from app.modules.email_verification.models import CodeEmail
from app.modules.password_recovery.models import PasswordRecovery
from app.modules.emails.models import EmailMessage, MessageStatus
from app.modules.catalogs.models import Catalog