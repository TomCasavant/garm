# Extends Platform, represents the Steam platform
from .platform import Platform
from steam_web_api import Steam
import os

# Implements get_achievements and get_screenshots for Steam
class SteamPlatform(Platform):
    def __init__(self):
        super().__init__('Steam')
        self.steam = self.create_steam_client()

    def get_achievements(self, game):
        pass

    def get_screenshots(self):
        screenshots_file_type = 4
        num_per_page = 10
        steam_id = os.getenv('STEAM_ID') #TODO: Can we get this from the Steam API?
        screenshots = self.steam.apps.get_user_files(steam_id, screenshots_file_type, num_per_page)
        print(screenshots)
        return screenshots

    def create_steam_client(self):
        key = os.getenv('STEAM_API_KEY')
        if key is None:
            raise Exception('STEAM_API_KEY not found')

        return Steam(key)