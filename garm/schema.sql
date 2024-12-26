DROP TABLE IF EXISTS actor;
CREATE TABLE actor (
    garm_id TEXT PRIMARY KEY,
    profile_image TEXT,
    profile_url TEXT,
    steam_id TEXT,
    created_at TEXT,
    steam_name TEXT,
    public_key TEXT,
    private_key TEXT
);