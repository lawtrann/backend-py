from fastapi import Depends
from sqlmodel import Session

from app.api.provider import NoScope, RequestScope
from app.core.uow import UnitOfWork
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository
from app.infra.db.session import engine, get_db
from app.infra.sqlmodel.refresh_token_repo import SQLModelRefreshTokenRepository
from app.infra.sqlmodel.uow import SQLModelUnitOfWork
from app.infra.sqlmodel.user_repo import SQLModelUserRepository


def _user_repo(session: Session = Depends(get_db)) -> UserRepository:
    return SQLModelUserRepository(session)


def _refresh_token_repo(session: Session = Depends(get_db)) -> RefreshTokenRepository:
    return SQLModelRefreshTokenRepository(session)


def _uow() -> UnitOfWork:
    return SQLModelUnitOfWork(engine)


UserRepo = RequestScope(UserRepository, _user_repo)
RefreshTokenRepo = RequestScope(RefreshTokenRepository, _refresh_token_repo)
UoW = NoScope(UnitOfWork, _uow)
