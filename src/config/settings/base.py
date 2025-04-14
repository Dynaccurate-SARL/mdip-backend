from typing import List


class BaseEnvs:
    CORS_ORIGINS: List[str] = ['*']
    CORS_HEADERS: List[str] = ['*']
    CORS_METHODS: List[str] = ['*']

    JWT_SECRET: str = 'thisissecret'
    JWT_ACCESS_EXPIRATION: int = 900  # 900 seconds = 15 minutes
    JWT_REFRESH_EXPIRATION: int = 1800  # 1800 seconds = 30 minutes

    DATABASE_URL: str
    DATABASE_ECHO: bool = False
