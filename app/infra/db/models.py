from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, String, Uuid, text
from sqlmodel import Field, Relationship, SQLModel

class Users(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('ix_users_email', 'email', postgresql_include=[], unique=True),
        Index('ix_users_username', 'username', postgresql_include=[], unique=True)
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    username: str = Field(sa_column=Column('username', String(50), nullable=False))
    email: str = Field(sa_column=Column('email', String(255), nullable=False))
    hashed_password: str = Field(sa_column=Column('hashed_password', String, nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime, nullable=False, server_default=text("(now() AT TIME ZONE 'utc'::text)")))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime, nullable=False, server_default=text("(now() AT TIME ZONE 'utc'::text)")))
    deleted_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('deleted_at', DateTime))

    refresh_tokens: list['RefreshTokens'] = Relationship(back_populates='user')


class RefreshTokens(SQLModel, table=True):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='refresh_tokens_user_id_fkey'),
        PrimaryKeyConstraint('id', name='refresh_tokens_pkey'),
        Index('ix_refresh_tokens_token_hash', 'token_hash', postgresql_include=[], unique=True)
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    token_hash: str = Field(sa_column=Column('token_hash', String, nullable=False))
    user_id: uuid.UUID = Field(sa_column=Column('user_id', Uuid, nullable=False))
    expires_at: datetime.datetime = Field(sa_column=Column('expires_at', DateTime, nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime, nullable=False, server_default=text("(now() AT TIME ZONE 'utc'::text)")))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime, nullable=False, server_default=text("(now() AT TIME ZONE 'utc'::text)")))
    revoked_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('revoked_at', DateTime))
    deleted_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('deleted_at', DateTime))

    user: 'Users' = Relationship(back_populates='refresh_tokens')
