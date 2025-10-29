CREATE TABLE IF NOT EXISTS used_ids (
    id TEXT PRIMARY KEY,
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ips (
    ip TEXT PRIMARY KEY,
    score INTEGER NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    salt TEXT NOT NULL,
    totp TEXT NOT NULL,
    roles TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_login TEXT NOT NULL,
    tos_accepted TEXT NOT NULL,
    balance INTEGER NOT NULL,
    theme TEXT NOT NULL,
    locale TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created TEXT NOT NULL,
    expires TEXT NOT NULL,
    browser TEXT NOT NULL
);
