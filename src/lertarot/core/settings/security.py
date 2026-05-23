"""Configurações de segurança"""
import os
from dotenv import load_dotenv

# Inicia o carregamento das variáveis de ambiente
load_dotenv()


class Settings:
    ENV = os.getenv("ENV", "TEST")

    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY
    
    @property
    def algorithm(self) -> str:
        return self.ALGORITHM
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
            


security_settings = Settings()

if __name__ == "__main__":
    print(security_settings.secret_key, security_settings.algorithm, security_settings.access_token_expire_minutes)