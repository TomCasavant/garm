import enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from pydantic.v1 import root_validator


class ObjectType(enum.Enum):
    Accept = "Accept"
    Actor = "Actor"
    Create = "Create"
    Follow = "Follow"
    Service = "Service"
    Note = "Note"
    Person = "Person"

class AttachmentType(enum.Enum):
    PropertyValue = "PropertyValue" # Used for profiles

class Attachment(BaseModel):
    type: AttachmentType
    name: str
    value: str

class PublicKey(BaseModel):
    id: str
    owner: str
    public_key_pem: str = Field(alias='publicKeyPem')

class Icon(BaseModel):
    type: str = 'Image'
    media_type: str = 'image/jpeg'
    url: str

class APObject(BaseModel):
    to: Union[str, List[str]] = None
    cc: Union[str, List[str]] = None
    name: Optional[str] = None
    content: Optional[str] = None
    content_map: Optional[dict] = Field(alias='contentMap')
    summary: Optional[str] = None
    attributed_to: Optional[str] = Field(alias='attributedTo')
    in_reply_to: Optional[str] = Field(alias='inReplyTo')
    updated: Optional[str] = None
    attachment: Optional[List] = None
    tag: Optional[List[str]] = None
    url: Optional[str] = None

    @root_validator(pre=True)
    def set_defaults(cls, values):
        values['to'] = values.get('to', [])
        values['cc'] = values.get('cc', [])
        values['contentMap'] = values.get('contentMap', {})
        values['attachment'] = values.get('attachment', [])
        values['tag'] = values.get('tag', [])
        return values


    def to_json(self) -> Dict:
        # Temporary to_json alias for model_dump
        return self.model_dump()

class Activity(APObject):
    id: str
    actor: str
    to: Union[str, List[str]]
    published: str
    type: ObjectType
    object: APObject
    cc: Union[str, List[str]] = None

    @root_validator(pre=True)
    def set_defaults(cls, values):
        values['cc'] = values.get('cc', [])
        return values

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'actor': self.actor,
            'to': self.to,
            'published': self.published,
            'type': self.type,
            'object': self.object,
            'cc': self.cc
        }

    def to_json(self) -> Dict:
        return self.to_dict()

class CreateActivity(Activity):
    type: ObjectType = Field(default=ObjectType.Create)

class FollowActivity(Activity):
    type: ObjectType = Field(default=ObjectType.Follow)

class AcceptActivity(Activity):
    type: ObjectType = Field(default=ObjectType.Accept)

class Note(APObject):
    id: str
    actor: str
    content: str
    to: Union[str, List[str]]
    published: str
    attributed_to: str = Field(alias='attributedTo')
    url: str
    type: ObjectType = Field(default=ObjectType.Note)

class BaseActor(BaseModel):
    id: str
    inbox: str
    outbox: str
    type: ObjectType = Field(default=ObjectType.Actor)

class Actor(BaseActor):
    featured: str = None
    featuredTags: Optional[str] = None
    preferredUsername: Optional[str] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    manuallyApprovesFollowers: Optional[bool] = None
    discoverable: Optional[bool] = None
    indexable: Optional[bool] = None
    published: Optional[str] = None
    memorial: Optional[bool] = None
    alsoKnownAs: Optional[list] = None
    attributionDomains: Optional[list] = None
    public_key: Optional[PublicKey] = Field(alias='publicKey')
    tag: Optional[list] = None
    attachment: Optional[list] = None
    endpoints: Optional[dict] = None
    icon: Optional[dict] = None
    image: Optional[dict] = None

