# Extends Platform, represents the Steam platform
from ugs.ap_models.screenshot import SteamScreenshot
from .models.activity import Activity
from .models.actor import Actor
from .models.screenshot import Screenshot
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
        user = Actor.query.filter_by(steam_id=steam_id).first()
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
                self.add_screenshot(screenshot, user.ugs_id)

            current_count += len(published_files)
            page += 1
            self.db.session.commit()

        print("Finished loading all screenshots.")

    def add_screenshot(self, screenshot, user_id):
        print("Adding screenshot to the database")
        guid, note = SteamScreenshot.from_screenshot_row(screenshot, user_id)
        print(f"Note creatd with GUID: {guid}")
        note_dump = note.model_dump(mode="json", by_alias=True)
        note_str = str(note_dump)

        # Check if screenshot is already in the database
        existing_screenshot = Screenshot.query.filter_by(steam_id=screenshot.get('publishedfileid')).first()
        if existing_screenshot:
            print(f"Screenshot ID: {existing_screenshot.steam_id} already exists in the database")
        else:
            new_screenshot = Screenshot(
                steam_id=screenshot.get('publishedfileid'),
                ugs_user=user_id,
                creator=screenshot.get('creator'),
                creator_appid=screenshot.get('creator_appid'),
                consumer_appid=screenshot.get('consumer_appid'),
                consumer_shortcutid=screenshot.get('consumer_shortcutid'),
                filename=screenshot.get('filename'),
                file_size=screenshot.get('file_size'),
                preview_file_size=screenshot.get('preview_file_size'),
                file_url=screenshot.get('file_url'),
                preview_url=screenshot.get('preview_url'),
                url=screenshot.get('url'),
                hcontent_file=screenshot.get('hcontent_file'),
                hcontent_preview=screenshot.get('hcontent_preview'),
                title=screenshot.get('title'),
                short_description=screenshot.get('short_description'),
                time_created=screenshot.get('time_created'),
                time_updated=screenshot.get('time_updated'),
                visibility=screenshot.get('visibility'),
                flags=screenshot.get('flags'),
                workshop_file=screenshot.get('workshop_file'),
                workshop_accepted=screenshot.get('workshop_accepted'),
                show_subscribe_all=screenshot.get('show_subscribe_all'),
                num_comments_developer=screenshot.get('num_comments_developer'),
                num_comments_public=screenshot.get('num_comments_public'),
                banned=screenshot.get('banned'),
                ban_reason=screenshot.get('ban_reason'),
                banner=screenshot.get('banner'),
                can_be_deleted=screenshot.get('can_be_deleted'),
                app_name=screenshot.get('app_name'),
                file_type=screenshot.get('file_type'),
                can_subscribe=screenshot.get('can_subscribe'),
                subscriptions=screenshot.get('subscriptions'),
                favorited=screenshot.get('favorited'),
                followers=screenshot.get('followers'),
                lifetime_subscriptions=screenshot.get('lifetime_subscriptions'),
                lifetime_favorited=screenshot.get('lifetime_favorited'),
                lifetime_followers=screenshot.get('lifetime_followers'),
                lifetime_playtime=screenshot.get('lifetime_playtime'),
                lifetime_playtime_sessions=screenshot.get('lifetime_playtime_sessions'),
                views=screenshot.get('views'),
                image_width=screenshot.get('image_width'),
                image_height=screenshot.get('image_height'),
                image_url=screenshot.get('image_url'),
                num_children=screenshot.get('num_children'),
                num_reports=screenshot.get('num_reports'),
                score=screenshot.get('score'),
                votes_up=screenshot.get('votes_up'),
                votes_down=screenshot.get('votes_down'),
                language=screenshot.get('language'),
                maybe_inappropriate_sex=screenshot.get('maybe_inappropriate_sex'),
                maybe_inappropriate_violence=screenshot.get('maybe_inappropriate_violence'),
                revision_change_number=screenshot.get('revision_change_number'),
                revision=screenshot.get('revision'),
                ban_text_check_result=screenshot.get('ban_text_check_result'),
                raw_activity=note_str
            )
            self.db.session.add(new_screenshot)
            self.db.session.commit()
            print(f"Processed screenshot GUID: {guid}")


        actor_guid = user_id
        activity_type = 'Note'
        object_guid = guid
        activity_json = note_str
        print("Adding activity to the database")

        if existing_screenshot:
            # Get the existing activity
            existing_activity = Activity.query.filter_by(screenshot_id=existing_screenshot.steam_id, activity_type='Note').first()
            if existing_activity:
                print(f"Activity for screenshot ID: {existing_screenshot.steam_id} already exists in the database")
                # Check if activity_json is the same
                # Convert activity_json and note_str to json dictionaries
                existing_activity_json = eval(existing_activity.activity_json)
                new_activity_json = eval(note_str)
                # Everything except url/id should be the same
                for key in existing_activity_json:
                    if key == 'url' or key == 'id':
                        continue
                    if existing_activity_json[key] != new_activity_json[key]:
                        print(f"Activity for screenshot ID: {existing_screenshot.steam_id} has been updated")
                        existing_activity.activity_json = note_str
                        existing_screenshot.raw_activity = note_str
                        self.db.session.commit()
                        break
        else:
            new_activity = Activity(
                guid=f"{guid}",
                actor_guid=actor_guid,
                activity_type=activity_type,
                object_guid=object_guid,
                activity_json=str(activity_json),
                screenshot_id=screenshot.get('publishedfileid')
            )
            self.db.session.add(new_activity)
            self.db.session.commit()

        print(f"Processed screenshot GUID: {guid}")

    def update_db(self):
        # Originally loaded in the first 10 screenshots, may return to this later
        pass

    def create_steam_client(self):
        key = os.getenv('STEAM_API_KEY')
        if key is None:
            raise Exception('STEAM_API_KEY not found')

        return Steam(key)
