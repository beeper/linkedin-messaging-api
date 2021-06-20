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

    def __repr__(self):
        return "URN({}:{})".format(
            self.prefix,
            self.id_parts[0]
            if len(self.id_parts) == 1
            else "(" + ",".join(self.id_parts) + ")",
        )


# Use milliseconds instead of seconds from the UNIX epoch.
decoder_functions = {
    datetime: (lambda s: datetime.fromtimestamp(int(s) / 1000) if s else None),
    URN: (lambda s: URN(s) if s else None),
}
encoder_functions = {
    datetime: (lambda d: int(d.timestamp() * 1000) if d else None),
    URN: (lambda u: u.id_parts[-1] if u else None),
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
class ConversationsResponseMetadata:
    unread_count: int


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ConversationsResponsePaging:
    count: int
    start: int
    links: List[Any]


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class AttributedBody:
    text: str


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class MessageEvent:
    message_body_render_format: str
    body: str
    attributed_body: AttributedBody


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
class ConversationEvent:
    created_at: datetime
    reaction_summaries: List[Any]
    entity_urn: URN
    event_content: EventContent
    subtype: str
    from_: From = field(metadata=config(field_name="from"))
    previous_event_in_conversation: Optional[URN] = None


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


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ConversationsResponse(DataClassJsonMixin):
    metadata: ConversationsResponseMetadata
    elements: List[Conversation]
    paging: ConversationsResponsePaging
