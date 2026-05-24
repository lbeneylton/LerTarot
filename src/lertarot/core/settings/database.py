"""Classes de configurações do banco
Se nao tiver nome do banco
usa o banco sqlite test.db
"""
import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self):
        self.host = os.getenv("DB_HOaST", None)
        self.name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT")

    @property
    def url_database(self):
        if not self.host:
            return "sqlite:///test.db"

        return (
            f"postgresql+psycopg://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


database_settings = Settings()

if __name__ == "__main__":
    print(database_settings.url_database)
