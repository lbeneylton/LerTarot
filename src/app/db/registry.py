"""Documento para encaminhar os models para o alembic"""
from app.domains.users.models import User, Client, Reader
from app.domains.providers.models import Provider, UserProvider
from app.domains.catalogs.models import Catalog
from app.domains.verify.models import CodeEmail
from providers.emails.model import EmailMessage

