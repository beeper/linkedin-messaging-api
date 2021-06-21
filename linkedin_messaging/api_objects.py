from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, List, Optional

import dataclasses_json
from dataclasses_json import (
    config,
    DataClassJsonMixin,
    dataclass_json,
    LetterCase,
    Undefined,
)


class URN:
    def __init__(self, urn_str: str):
        urn_parts = urn_str.split(":")
        self.prefix = ":".join(urn_parts[:-1])
        self.id_parts = urn_parts[-1].strip("()").split(",")

    def get_id(self):
        assert len(self.id_parts) == 1
        return self.id_parts[0]

    def __str__(self):
        return "{}:{}".format(
            self.prefix,
            (
                self.id_parts[0]
                if len(self.id_parts) == 1
                else "(" + ",".join(self.id_parts) + ")"
            ),
        )

    def __repr__(self):
        return f"URN('{str(self)}')"


# Use milliseconds instead of seconds from the UNIX epoch.
decoder_functions = {
    datetime: (lambda s: datetime.fromtimestamp(int(s) / 1000) if s else None),
    URN: (lambda s: URN(s) if s else None),
}
encoder_functions = {
    datetime: (lambda d: int(d.timestamp() * 1000) if d else None),
    URN: (lambda u: str(u) if u else None),
}

for type_, translation_function in decoder_functions.items():
    dataclasses_json.cfg.global_config.decoders[type_] = translation_function
    dataclasses_json.cfg.global_config.decoders[
        Optional[type_]  # type: ignore
    ] = translation_function

for type_, translation_function in encoder_functions.items():
    dataclasses_json.cfg.global_config.encoders[type_] = translation_function
    dataclasses_json.cfg.global_config.encoders[
        Optional[type_]  # type: ignore
    ] = translation_function


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Artifact:
    width: int
    height: int
    file_identifying_url_path_segment: str
    expires_at: datetime


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class VectorImage:
    artifacts: List[Artifact]
    root_url: str


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Picture:
    vector_image: VectorImage = field(
        metadata=config(field_name="com.linkedin.common.VectorImage")
    )


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class MiniProfile:
    first_name: str
    last_name: str
    occupation: str
    entity_urn: URN
    public_identifier: str
    tracking_id: str

    memorialized: bool = False
    picture: Optional[Picture] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class MessagingMember:
    mini_profile: MiniProfile
    entity_urn: URN


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Paging:
    count: int
    start: int
    links: List[Any]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TextEntity:
    urn: URN


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttributeType:
    text_entity: TextEntity = field(
        metadata=config(field_name="com.linkedin.pemberly.text.Entity")
    )


@dataclass_json
@dataclass
class Attribute:
    start: int
    length: int
    type_: AttributeType = field(metadata=config(field_name="type"))


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class AttributedBody:
    text: str = ""
    attributes: List[Attribute] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageAttachmentCreate:
    byte_size: int
    id_: URN = field(metadata=config(field_name="id"))
    media_type: str
    name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageAttachmentReference:
    string: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageAttachment:
    byte_size: int
    id_: URN = field(metadata=config(field_name="id"))
    media_type: str
    name: str
    reference: MessageAttachmentReference


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GifInfo:
    original_height: int
    original_width: int
    url: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ThirdPartyMediaInfo:
    previewgif: GifInfo
    nanogif: GifInfo
    gif: GifInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ThirdPartyMedia:
    media_type: str
    id_: str = field(metadata=config(field_name="id"))
    media: ThirdPartyMediaInfo
    title: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageCustomContent:
    third_party_media: ThirdPartyMedia = field(
        metadata=config(
            field_name="com.linkedin.voyager.messaging.shared.ThirdPartyMedia"
        )
    )


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageEvent:
    attributed_body: AttributedBody
    body: str
    message_body_render_format: str
    attachments: List[MessageAttachment] = field(default_factory=list)
    custom_content: Optional[MessageCustomContent] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class EventContent:
    message_event: MessageEvent = field(
        metadata=config(field_name="com.linkedin.voyager.messaging.event.MessageEvent")
    )


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class From:
    messaging_member: MessagingMember = field(
        metadata=config(field_name="com.linkedin.voyager.messaging.MessagingMember")
    )


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ReactionSummary:
    count: int
    first_reacted_at: datetime
    emoji: str
    viewer_reacted: bool


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ConversationEvent:
    created_at: datetime
    entity_urn: URN
    event_content: EventContent
    subtype: str
    from_: From = field(metadata=config(field_name="from"))
    previous_event_in_conversation: Optional[URN] = None
    reaction_summaries: List[ReactionSummary] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Participant:
    messaging_member: MessagingMember = field(
        metadata=config(field_name="com.linkedin.voyager.messaging.MessagingMember")
    )


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Conversation:
    group_chat: bool
    total_event_count: int
    unread_count: int
    last_activity_at: datetime
    entity_urn: URN
    muted: bool
    events: List[ConversationEvent]
    participants: List[Participant]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConversationsResponse(DataClassJsonMixin):
    elements: List[Conversation]
    paging: Paging


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConversationResponse(DataClassJsonMixin):
    elements: List[ConversationEvent]
    paging: Paging


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageCreate(DataClassJsonMixin):
    attributed_body: AttributedBody
    body: str = ""
    attachments: List[MessageAttachmentCreate] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageCreatedInfo:
    created_at: datetime
    event_urn: URN
    backend_event_urn: URN
    conversation_urn: URN
    backend_conversation_urn: URN


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SendMessageResponse(DataClassJsonMixin):
    value: MessageCreatedInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserProfileResponse(DataClassJsonMixin):
    plain_id: str
    mini_profile: MiniProfile
