-- initialize tables
-- Revision: 0137f9597dca
-- Downgrade SQL

DROP INDEX IF EXISTS ix_refresh_tokens_token_hash;
DROP TABLE IF EXISTS refresh_tokens;

DROP INDEX IF EXISTS ix_users_username;
DROP INDEX IF EXISTS ix_users_email;
DROP TABLE IF EXISTS users;
