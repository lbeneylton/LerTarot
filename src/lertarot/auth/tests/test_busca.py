from lertarot.auth.repo import UserRepo
from lertarot.core.database.models import Users

def test_get_user_by_id(session):
    repo = UserRepo(session)

    user = Users(
        nome="Maria",
        email="maria@email.com",
        senha_hash="dasdasd"
    )

    created = repo.create(user)

    found = repo.get_by_id(created.user_id)

    assert found is not None
    assert found.email == "maria@email.com"