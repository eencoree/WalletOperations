"""Configuration for connecting to the database"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    The class provides a function to create a database URL for connection.
    Values are loaded from the .env file

    Attributes:
        DB_USER (str): The database user name.
        DB_PASSWORD (str): The database password.
        DB_HOST (str): The database host name.
        DB_PORT (int): The database port.
        DB_NAME (str): The database name.
        TEST (str): Adding a database to the name of the test.
    """

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    TEST: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", load_dotenv=True
    )

    def get_db_url(self) -> str:
        """
        The function that creates the database URL
        :return: database URL
        """

        dbname = f"{self.DB_NAME}{self.TEST or ''}"
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{dbname}"
        )


settings = Settings()
