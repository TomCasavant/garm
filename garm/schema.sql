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

DROP TABLE IF EXISTS foreign_actor;
CREATE TABLE foreign_actor (
    ap_id TEXT PRIMARY KEY,
    name TEXT,
    preferred_username TEXT,
    inbox TEXT,
    public_key TEXT
);

DROP TABLE IF EXISTS foreign_activity;
CREATE TABLE foreign_activity (
    activity_id TEXT PRIMARY KEY,
    activity_type TEXT,
    foreign_actor_id TEXT,
    subject_actor_guid TEXT,
    datetime_created TEXT,
    raw_activity TEXT,
    FOREIGN KEY(foreign_actor_id) REFERENCES foreign_actor(ap_id)
);

-- Generic Activity Table, we should store the activity's guid,
-- the local actor, the activity type, optional object (object will just be a reference to another activity),
-- and the complete activity json
DROP TABLE IF EXISTS activity;
CREATE TABLE activity (
    guid TEXT PRIMARY KEY,
    actor_guid TEXT,
    activity_type TEXT,
    object_guid TEXT,
    activity_json TEXT,
    screenshot_id TEXT,
    FOREIGN KEY(actor_guid) REFERENCES actor(garm_id),
    FOREIGN KEY(object_guid) REFERENCES activity(guid)
);

DROP TABLE IF EXISTS screenshot;
CREATE TABLE screenshot (
    steam_id TEXT PRIMARY KEY,
    creator TEXT,
    creator_appid TEXT,
    consumer_appid TEXT,
    consumer_shortcutid TEXT,
    filename TEXT,
    file_size TEXT,
    preview_file_size TEXT,
    file_url TEXT,
    preview_url TEXT,
    url TEXT,
    hcontent_file TEXT,
    hcontent_preview TEXT,
    title TEXT,
    short_description TEXT,
    time_created TEXT,
    time_updated TEXT,
    visibility TEXT,
    flags TEXT,
    workshop_file TEXT,
    workshop_accepted TEXT,
    show_subscribe_all TEXT,
    num_comments_developer TEXT,
    num_comments_public TEXT,
    banned TEXT,
    ban_reason TEXT,
    banner TEXT,
    can_be_deleted TEXT,
    app_name TEXT,
    file_type TEXT,
    can_subscribe TEXT,
    subscriptions TEXT,
    favorited TEXT,
    followers TEXT,
    lifetime_subscriptions TEXT,
    lifetime_favorited TEXT,
    lifetime_followers TEXT,
    lifetime_playtime TEXT,
    lifetime_playtime_sessions TEXT,
    views TEXT,
    image_width TEXT,
    image_height TEXT,
    image_url TEXT,
    num_children TEXT,
    num_reports TEXT,
    score TEXT,
    votes_up TEXT,
    votes_down TEXT,
    language TEXT,
    maybe_inappropriate_sex TEXT,
    maybe_inappropriate_violence TEXT,
    revision_change_number TEXT,
    revision TEXT,
    ban_text_check_result TEXT,
    raw_activity TEXT
);

-- Followers Table, should store a list of users (that reference foreign_actor), followed by the guid of the actor they are following
DROP TABLE IF EXISTS followers;
CREATE TABLE followers (
    follower_id TEXT,
    following_id TEXT,
    FOREIGN KEY(follower_id) REFERENCES foreign_actor(ap_id),
    FOREIGN KEY(following_id) REFERENCES actor(garm_id)
);