from lertarot.auth.repo import UserRepo
from lertarot.core.database.models import Users


def test_create_user(session):
    repo = UserRepo(session)

    user = Users(
        nome="João",
        email="joao@email.com",
        senha_hash="asdsad"
    )

    created_user = repo.create(user)

    assert created_user.user_id is not None
    assert created_user.nome == "João"