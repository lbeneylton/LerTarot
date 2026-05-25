from sqlalchemy.orm import Session
from lertarot.core.database.models import Users, Readers, Clients


class UserRepo:
    """Repositório base para usuários"""
     
    def __init__(self, session: Session)-> None:
        self.session = session
        
        
    def create(self, usuario: Users):
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        
        return usuario
    
    def get_by_id(self, user_id):
        return (
            self.session.query(Users)
            .filter(Users.user_id == user_id)
            .first()
        )
    
    

class ClientRepo(UserRepo):
    """Repositório específico para clientes"""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, client: Clients):
        return super().create(client)

    def get_all(self):
        return self.session.query(Clients).all()
    
    

class ReaderRepo(UserRepo):
    """Repositório específico para leitores"""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, reader: Readers):
        return super().create(reader)

    def get_all(self):
        return self.session.query(Readers).all()

    def get_by_speciality(self, speciality_id):
        return (
            self.session.query(Readers)
            .join(Readers.fk_speciality)
            .filter_by(speciality_id=speciality_id)
            .all()
        )       
    