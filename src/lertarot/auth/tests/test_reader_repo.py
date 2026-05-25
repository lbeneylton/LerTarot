from lertarot.auth.repo import ReaderRepo
from lertarot.core.database.models import Readers


def test_create_reader(session):
    repo = ReaderRepo(session)

    reader = Readers(
        nome="Tarólogo",
        email="reader@email.com",
        senha_hash="123456",
        foto_url="foto.jpg",
        bio="Tarólogo especialista"
    )

    created_reader = repo.create(reader)

    assert created_reader.fk_user_id is not None
    assert created_reader.bio == "Tarólogo especialista"
    assert created_reader.foto_url == "foto.jpg"