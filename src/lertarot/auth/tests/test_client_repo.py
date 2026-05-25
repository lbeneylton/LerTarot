from lertarot.auth.repo import ClientRepo
from lertarot.core.database.models import Clients


def test_create_client(session):
    repo = ClientRepo(session)

    client = Clients(
        nome="Cliente",
        email="cliente@email.com",
        senha_hash="123456"
    )

    created_client = repo.create(client)

    assert created_client.fk_user_id is not None