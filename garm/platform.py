# Base class that represents a game platform (steam, epic, retroachievements, etc)
# Common methods that will convert platform activities into ActivityPub objects
# e.g. get_achievements -> ActivityPub objects, get_screenshots, etc.
class Platform:
    def __init__(self, name):
        self.name = name

    def get_achievements(self, game):
        pass

    def get_screenshots(self):
        pass