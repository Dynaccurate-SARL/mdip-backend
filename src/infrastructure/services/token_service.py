import jwt

from typing import List, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


ALGORITHM = "HS256"


@dataclass
class TokenPayload:
    sub: str
    scopes: List[str]
    extra: Dict | None


class TokenServiceInterface(ABC):
    """Interface for TokenServices."""
    @abstractmethod
    def generate_token(self, sub: str, scopes: List[str],
                       extra: Dict = None,
                       expiration: datetime = None) -> str:
        pass

    @abstractmethod
    def get_token_payload(self, token: str) -> TokenPayload:
        pass


class IAccessTokenService(TokenServiceInterface):
    """Generate and validate access token.

    Arguments:
        secret_key (str): The secret used to sign and decrypt the JWT
        algorithm (str): Should be "HS256" or "RS256" used to decrypt the JWT
        expiration (expiration): Seconds to expire. The default expiration time of the token, defaults to 1 hour
    """

    def __init__(
        self,
        secret_key: str,
        expiration: float = 3600,
        algorithm: str = ALGORITHM,
    ):
        self._secret_key = secret_key
        self._expiration = expiration
        self._algorithm = algorithm

    def generate_token(self, sub: str, scopes: List[str],
                       extra: Dict = None,
                       expiration: datetime = None) -> str:
        # Set the expiration time to the default if not provided
        if expiration is None:
            expiration = datetime.now(timezone.utc) + timedelta(
                seconds=self._expiration
            )

        # Create the payload with the user ID and expiration time
        payload = {'sub': sub, 'scopes': scopes, 'exp': expiration}
        if extra:
            payload.update({"extra": extra})

        # Generate the token using the JWT library
        token = jwt.encode(payload, self._secret_key,
                           algorithm=self._algorithm)
        return token

    def get_token_payload(self, token: str) -> TokenPayload:
        payload: Dict = jwt.decode(
            token, self._secret_key, algorithms=[self._algorithm])
        return TokenPayload(
            sub=payload.get("sub"),
            scopes=payload.get("scopes", []),
            extra=payload.get("extra", None),
        )


class IRefreshTokenService(TokenServiceInterface):
    """Generate and validate refresh token.

    Arguments:
        secret_key (str): The secret used to sign and decrypt the JWT
        algorithm (str): Should be "HS256" or "RS256" used to decrypt the JWT
        expiration (expiration): Seconds to expire. The default expiration time of the token, defaults to 2 hours
    """

    def __init__(
        self,
        secret_key: str,
        expiration: float = 7200,
        algorithm: str = ALGORITHM,
    ):
        self._secret_key = secret_key
        self._expiration = expiration
        self._algorithm = algorithm

    def generate_token(self, sub: str, expiration: datetime = None) -> str:
        # Set the expiration time to the default if not provided
        if expiration is None:
            expiration = datetime.now(timezone.utc) + timedelta(
                seconds=self._expiration
            )

        # Create the payload with the user ID and expiration time
        payload = {'sub': sub, 'exp': expiration}

        # Generate the token using the JWT library
        token = jwt.encode(payload, self._secret_key,
                           algorithm=self._algorithm)
        return token

    def get_token_payload(self, token: str) -> TokenPayload:
        # Decode the token using the JWT library
        payload: Dict = jwt.decode(
            token, self._secret_key, algorithms=[self._algorithm]
        )
        return TokenPayload(
            sub=payload.get("sub"),
            scopes=payload.get("scopes", []),
            extra=payload.get("extra", None),
        )
