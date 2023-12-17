from uuid import UUID
from pydantic import BaseModel
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException

# cookieの設定
cookie_params = CookieParameters(samesite="none")

cookie = SessionCookie(
    cookie_name="session",
    identifier="general_verifier",
    auto_error=False,
    secret_key="secret",
    cookie_params=cookie_params,
)

# セッション周り
class SessionData(BaseModel):
    access_token: str

backend = InMemoryBackend[UUID, SessionData]()

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


session_verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=False,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)