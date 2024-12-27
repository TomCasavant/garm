# Extends Platform, represents the Steam platform
from .models.screenshot import SteamScreenshot
from .platform import Platform
from steam_web_api import Steam
import os

#TODO: Move to separate class

STEAM_FILEPATH = "https://steamcommunity.com/sharedfiles/filedetails/?id={}"

# Implements get_achievements and get_screenshots for Steam
class SteamPlatform(Platform):
    def __init__(self, db=None):
        super().__init__('Steam')
        self.steam = self.create_steam_client()
        self.db = db

    def get_achievements(self, game):
        pass

    def get_screenshots(self):
        screenshots_file_type = 4
        num_per_page = 10
        steam_id = os.getenv('STEAM_ID') #TODO: Can we get this from the Steam API?
        screenshots = self.steam.apps.get_user_files(steam_id, screenshots_file_type, num_per_page)
        print(screenshots)
        return screenshots

    def update_db(self):
        # Gets the most recent 10 screenshots, and updates the database
        screenshots = self.get_screenshots()

        db = self.db
        for screenshot in screenshots['response']['publishedfiledetails']: # screenshot is of type dict

            guid, note = SteamScreenshot.from_screenshot_row(screenshot)
            # convert to string
            note_dump = note.model_dump(mode="json", by_alias=True)
            note_str = str(note_dump)


            db.execute(
                'INSERT INTO screenshot (steam_id, creator, creator_appid, consumer_appid, consumer_shortcutid, filename, file_size, preview_file_size, file_url, preview_url, url, hcontent_file, hcontent_preview, title, short_description, time_created, time_updated, visibility, flags, workshop_file, workshop_accepted, show_subscribe_all, num_comments_developer, num_comments_public, banned, ban_reason, banner, can_be_deleted, app_name, file_type, can_subscribe, subscriptions, favorited, followers, lifetime_subscriptions, lifetime_favorited, lifetime_followers, lifetime_playtime, lifetime_playtime_sessions, views, image_width, image_height, image_url, num_children, num_reports, score, votes_up, votes_down, language, maybe_inappropriate_sex, maybe_inappropriate_violence, revision_change_number, revision, ban_text_check_result, raw_activity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    screenshot.get('steam_id'),
                    screenshot.get('creator'),
                    screenshot.get('creator_appid'),
                    screenshot.get('consumer_appid'),
                    screenshot.get('consumer_shortcutid'),
                    screenshot.get('filename'),
                    screenshot.get('file_size'),
                    screenshot.get('preview_file_size'),
                    screenshot.get('file_url'),
                    screenshot.get('preview_url'),
                    screenshot.get('url'),
                    screenshot.get('hcontent_file'),
                    screenshot.get('hcontent_preview'),
                    screenshot.get('title'),
                    screenshot.get('short_description'),
                    screenshot.get('time_created'),
                    screenshot.get('time_updated'),
                    screenshot.get('visibility'),
                    screenshot.get('flags'),
                    screenshot.get('workshop_file'),
                    screenshot.get('workshop_accepted'),
                    screenshot.get('show_subscribe_all'),
                    screenshot.get('num_comments_developer'),
                    screenshot.get('num_comments_public'),
                    screenshot.get('banned'),
                    screenshot.get('ban_reason'),
                    screenshot.get('banner'),
                    screenshot.get('can_be_deleted'),
                    screenshot.get('app_name'),
                    screenshot.get('file_type'),
                    screenshot.get('can_subscribe'),
                    screenshot.get('subscriptions'),
                    screenshot.get('favorited'),
                    screenshot.get('followers'),
                    screenshot.get('lifetime_subscriptions'),
                    screenshot.get('lifetime_favorited'),
                    screenshot.get('lifetime_followers'),
                    screenshot.get('lifetime_playtime'),
                    screenshot.get('lifetime_playtime_sessions'),
                    screenshot.get('views'),
                    screenshot.get('image_width'),
                    screenshot.get('image_height'),
                    screenshot.get('image_url'),
                    screenshot.get('num_children'),
                    screenshot.get('num_reports'),
                    screenshot.get('score'),
                    screenshot.get('votes_up'),
                    screenshot.get('votes_down'),
                    screenshot.get('language'),
                    screenshot.get('maybe_inappropriate'),
                    screenshot.get('maybe_inappropriate_violence'),
                    screenshot.get('revision_change_number'),
                    screenshot.get('revision'),
                    screenshot.get('ban_text_check_result'),
                    note_str
                )
            )

            # Add the activity to the activity table
            # # Store the activity in the database
            #     db.execute(
            #         'INSERT INTO activity (guid, actor_guid, activity_type, object_guid, activity_json) VALUES (?, ?, ?, ?, ?)',
            #         (str(accept_guid), actor_obj['steam_name'], 'Accept', foreign_activity_id, str(accept))
            #     )

            actor_guid = 'MrPresidentTom'
            activity_type = 'Note'
            object_guid = guid
            activity_json = note_str
            db.execute(
                'INSERT INTO activity (guid, actor_guid, activity_type, object_guid, activity_json) VALUES (?, ?, ?, ?, ?)',
                (guid, actor_guid, activity_type, object_guid, activity_json)
            )
        db.commit()

    def create_steam_client(self):
        key = os.getenv('STEAM_API_KEY')
        if key is None:
            raise Exception('STEAM_API_KEY not found')

        return Steam(key)
