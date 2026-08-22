"""Documento para encaminhar os models para o alembic"""
from app.domains.users.models import User, Client, Reader
from app.domains.catalogs.models import Catalog
from app.domains.verify.models import CodeEmail
from app.domains.emails.model import EmailMessage

from app.domains.users.values.providers.models import Provider
from app.domains.users.values.password_recovery.models import PasswordRecovery