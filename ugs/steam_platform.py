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
        num_per_page = 250
        steam_id = os.getenv('STEAM_ID') #TODO: Can we get this from the Steam API?
        screenshots = self.steam.apps.get_user_files(steam_id, screenshots_file_type, num_per_page, 1)
        return screenshots

    def load_all_screenshots(self):
        print("Loading all screenshots into the database")

        steam_id = os.getenv('STEAM_ID')
        # Get user from actor table, match with steam_id
        user = self.db.execute('SELECT * FROM actor WHERE steam_id = ?', (steam_id,)).fetchone()

        if not user:
            print("User not found in the database.")
            return

        page = 1
        batch_size = 50
        screenshots = self.steam.apps.get_user_files(steam_id, 4, batch_size, page)

        if not screenshots or 'response' not in screenshots:
            print("No screenshots found or invalid response.")
            return

        total_count = screenshots['response'].get('total', 0)
        current_count = 0

        print(f"Total screenshots: {total_count}")

        while current_count < total_count:
            print(f"Processing page: {page}")

            screenshots = self.steam.apps.get_user_files(steam_id, 4, batch_size, page)
            if not screenshots or 'response' not in screenshots or 'publishedfiledetails' not in screenshots[
                'response']:
                print("Invalid or incomplete data received.")
                break

            published_files = screenshots['response']['publishedfiledetails']
            for screenshot in published_files:
                self.add_screenshot(screenshot, user['ugs_id'])

            current_count += len(published_files)
            page += 1
            self.db.commit()

        print("Finished loading all screenshots.")

    def add_screenshot(self, screenshot, user_id):
        guid, note = SteamScreenshot.from_screenshot_row(screenshot, user_id)
        note_dump = note.model_dump(mode="json", by_alias=True)
        note_str = str(note_dump)

        self.db.execute(
            'INSERT INTO screenshot (steam_id, ugs_user, creator, creator_appid, consumer_appid, consumer_shortcutid, filename, file_size, preview_file_size, file_url, preview_url, url, hcontent_file, hcontent_preview, title, short_description, time_created, time_updated, visibility, flags, workshop_file, workshop_accepted, show_subscribe_all, num_comments_developer, num_comments_public, banned, ban_reason, banner, can_be_deleted, app_name, file_type, can_subscribe, subscriptions, favorited, followers, lifetime_subscriptions, lifetime_favorited, lifetime_followers, lifetime_playtime, lifetime_playtime_sessions, views, image_width, image_height, image_url, num_children, num_reports, score, votes_up, votes_down, language, maybe_inappropriate_sex, maybe_inappropriate_violence, revision_change_number, revision, ban_text_check_result, raw_activity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                screenshot.get('publishedfileid'),
                user_id,
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
                screenshot.get('maybe_inappropriate_sex'),
                screenshot.get('maybe_inappropriate_violence'),
                screenshot.get('revision_change_number'),
                screenshot.get('revision'),
                screenshot.get('ban_text_check_result'),
                note_str
            )
        )

        actor_guid = user_id
        activity_type = 'Note'
        object_guid = guid
        activity_json = note_str
        self.db.execute(
            'INSERT INTO activity (guid, actor_guid, activity_type, object_guid, activity_json, screenshot_id) VALUES (?, ?, ?, ?, ?, ?)',
            (guid, actor_guid, activity_type, object_guid, activity_json, screenshot.get('publishedfileid'))
        )

        print(f"Processed screenshot GUID: {guid}")

    def update_db(self):
        # Originally loaded in the first 10 screenshots, may return to this later
        pass

    def create_steam_client(self):
        key = os.getenv('STEAM_API_KEY')
        if key is None:
            raise Exception('STEAM_API_KEY not found')

        return Steam(key)
