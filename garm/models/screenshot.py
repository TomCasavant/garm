"""
An AP Note object with an attachment that represents a screenshot.
"""
import uuid
from typing import Tuple

from garm.activitypub.models.activity import Note, AudienceType
from datetime import datetime

base_url = 'https://1f1b-2603-6010-c606-5f37-00-17ee.ngrok-free.app'

class ScreenshotNote(Note):
    """
    Represents a basic screenshot object.
    """

    @classmethod
    def from_screenshot_row(cls, screenshot_row: dict) -> Tuple[str, "ScreenshotNote"]:
        """
        Create a basic Screenshot instance from a database row.
        This should be overridden by subclasses for specific implementations.
        """
        raise NotImplementedError("Subclasses must implement from_screenshot_row")

    @classmethod
    def format_published_date(cls, unix_timestamp: int) -> str:
        """
        Convert a Unix timestamp to ActivityPub-compliant format.
        """
        return datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

    # generates/stores guid using uuid.uuid4()
    @classmethod
    def generate_guid(cls) -> str:
        """
        Generate a GUID for the screenshot.
        """
        return str(uuid.uuid4())

    # Creates a formatted id path /activities/uuid
    @classmethod
    def generate_id(cls, guid: str) -> str:
        """
        Generate an ID for the screenshot.
        """
        return base_url + f"/activities/{guid}"


class SteamScreenshot(ScreenshotNote):
    """
    Represents a Steam-specific screenshot note AP object.
    """

    @classmethod
    def from_screenshot_row(cls, screenshot_row: dict) -> Tuple[str, "ScreenshotNote"]:
        """
        Use this method to create a ScreenshotNote instance from the database row.
        """
        guid = cls.generate_guid()
        _id = cls.generate_id(guid)
        published = cls.format_published_date(screenshot_row['time_created'])

        screenshot_note = Note.model_validate({
            'id': _id,
            'type': 'Note',
            'summary': None,
            'inReplyTo': None,
            'published': published,
            'attributedTo': base_url + f"/user/MrPresidentTom",
            'to': [AudienceType.Public],
            'cc': base_url + f"/user/MrPresidentTom/followers",
            'sensitive': False,
            'content': screenshot_row['app_name'],
            'contentMap': {'en': ""},
            'attachment': [{
                'type': 'Document',
                'mediaType': 'image/jpeg',
                'url': screenshot_row['image_url'],
                'name': f"Screenshot of {screenshot_row['app_name']}"
            }],
            'url': _id,
            'actor': base_url + f"/user/MrPresidentTom",
            'tag': []
        })

        return guid, screenshot_note


