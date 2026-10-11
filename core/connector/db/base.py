from pydantic import SecretStr
from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str
    timeout: float = 30.0
