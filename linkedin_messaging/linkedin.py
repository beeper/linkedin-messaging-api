import json
import logging
import pickle
from collections import defaultdict
from datetime import datetime
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    Dict,
    List,
    Optional,
    Union,
)

import aiohttp
from bs4 import BeautifulSoup
from dataclasses_json import DataClassJsonMixin

from .api_objects import (
    ConversationEvent,
    ConversationResponse,
    ConversationsResponse,
    MessageAttachmentCreate,
    MessageCreate,
    Picture,
    ReactionSummary,
    SendMessageResponse,
    URN,
    UserProfileResponse,
)

REQUEST_HEADERS = {
    "user-agent": " ".join(
        [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/83.0.4103.116 Safari/537.36",
        ]
    ),
    # "accept": "application/vnd.linkedin.normalized+json+2.1",
    "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0",
    "x-li-track": json.dumps(
        {
            "clientVersion": "1.2.6216",
            "osName": "web",
            "timezoneOffset": 10,
            "deviceFormFactor": "DESKTOP",
            "mpName": "voyager-web",
        }
    ),
}

# URL to seed all of the auth requests
SEED_URL = "https://www.linkedin.com/uas/login"
LOGIN_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
VERIFY_URL = "https://www.linkedin.com/checkpoint/challenge/verify"

LINKEDIN_BASE_URL = "https://www.linkedin.com"
API_BASE_URL = f"{LINKEDIN_BASE_URL}/voyager/api"


class ChallengeException(Exception):
    pass


class LinkedInMessaging:
    session: aiohttp.ClientSession
    two_factor_payload: Dict[str, Any]
    event_listeners: DefaultDict[str, List[Callable[[Any], Awaitable[None]]]]

    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.event_listeners = defaultdict(list)

    @staticmethod
    def from_pickle(pickle_str: bytes) -> "LinkedInMessaging":
        linkedin = LinkedInMessaging()
        linkedin.session.cookie_jar._cookies = pickle.loads(pickle_str)
        for c in linkedin.session.cookie_jar:
            if c.key == "JSESSIONID":
                linkedin.session.headers["csrf-token"] = c.value.strip('"')
        return linkedin

    def to_pickle(self) -> bytes:
        return pickle.dumps(self.session.cookie_jar._cookies)

    async def close(self):
        await self.session.close()

    async def _get(self, relative_url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.session.get(API_BASE_URL + relative_url, **kwargs)

    async def _post(self, relative_url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.session.post(API_BASE_URL + relative_url, **kwargs)

    # region Authentication

    async def logged_in(self) -> bool:
        cookie_names = {c.key for c in self.session.cookie_jar}
        if (
            "liap" not in cookie_names
            or "li_at" not in cookie_names
            or "JSESSIONID" not in cookie_names
        ):
            return False
        return bool(await self.get_user_profile())

    async def login(self, email: str, password: str):
        # Get the CSRF token.
        async with self.session.get(SEED_URL) as seed_response:
            if seed_response.status != 200:
                raise Exception("Couldn't open the CSRF seed page")

            soup = BeautifulSoup(await seed_response.text(), "html.parser")
            login_csrf_param = soup.find("input", {"name": "loginCsrfParam"})["value"]

        # Login with username and password
        async with self.session.post(
            LOGIN_URL,
            data={
                "loginCsrfParam": login_csrf_param,
                "session_key": email,
                "session_password": password,
            },
        ) as login_response:
            # Check to see if the user was successfully logged in with just email and
            # password.
            if self.logged_in():
                for c in self.session.cookie_jar:
                    if c.key == "JSESSIONID":
                        self.session.headers["csrf-token"] = c.value.strip('"')
                return

            # 2FA is required. Throw an exception.
            soup = BeautifulSoup(await login_response.text(), "html.parser")

            # TODO better detection of 2FA vs bad password
            if soup.find("input", {"name": "challengeId"}):
                self.two_factor_payload = {
                    k: soup.find("input", {"name": k})["value"]
                    for k in (
                        "csrfToken",
                        "pageInstance",
                        "resendUrl",
                        "challengeId",
                        "displayTime",
                        "challengeSource",
                        "requestSubmissionId",
                        "challengeType",
                        "challengeData",
                        "challengeDetails",
                        "failureRedirectUri",
                    )
                }
                self.two_factor_payload["language"] = ("en-US",)
                raise ChallengeException()

            # TODO can we scrape anything from the page?
            raise Exception("Failed to log in.")

    async def enter_2fa(self, two_factor_code: str):
        async with self.session.post(
            VERIFY_URL, data={**self.two_factor_payload, "pin": two_factor_code}
        ):
            if self.logged_in():
                for c in self.session.cookie_jar:
                    if c.key == "JSESSIONID":
                        self.session.headers["csrf-token"] = c.value.strip('"')
                return
            # TODO can we scrape anything from the page?
            raise Exception("Failed to log in.")

    # endregion

    # region Conversations

    async def get_conversations(
        self,
        last_activity_before: Optional[datetime] = None,
    ) -> ConversationsResponse:
        """
        Fetch list of conversations the user is in.

        :param last_activity_before: :class:`datetime` of the last chat activity to
            consider
        """
        if last_activity_before is None:
            last_activity_before = datetime.now()

        params = {
            "keyVersion": "LEGACY_INBOX",
            # For some reason, createdBefore is the key, even though that makes
            # absolutely no sense whatsoever.
            "createdBefore": int(last_activity_before.timestamp() * 1000),
        }

        conversations_resp = await self._get("/messaging/conversations", params=params)
        return ConversationsResponse.from_json(await conversations_resp.text())

    async def get_conversation(
        self,
        conversation_urn: URN,
        created_before: Optional[datetime] = None,
    ) -> ConversationResponse:
        """
        Fetch the given conversation.

        :param conversation_urn_id: LinkedIn URN for a conversation
        :param created_before: datetime of the last chat activity to consider
        """
        if len(conversation_urn.id_parts) != 1:
            raise TypeError(f"Invalid conversation URN {conversation_urn}.")

        if created_before is None:
            created_before = datetime.now()

        params = {
            "createdBefore": int(created_before.timestamp() * 1000),
        }

        conversations_resp = await self._get(
            f"/messaging/conversations/{conversation_urn.id_parts[0]}/events",
            params=params,
        )
        return ConversationResponse.from_json(await conversations_resp.text())

    async def upload_media(
        self,
        data: bytes,
        filename: str,
        media_type: str,
    ) -> MessageAttachmentCreate:
        upload_metadata_response = await self._post(
            "/voyagerMediaUploadMetadata",
            params={"action": "upload"},
            json={
                "mediaUploadType": "MESSAGING_PHOTO_ATTACHMENT",
                "fileSize": len(data),
                "filename": filename,
            },
        )
        if upload_metadata_response.status != 200:
            raise Exception("Failed to send upload metadata.")

        upload_metadata_response_json = (await upload_metadata_response.json()).get(
            "value", {}
        )
        upload_url = upload_metadata_response_json.get("singleUploadUrl")
        if not upload_url:
            raise Exception("No upload URL provided")

        upload_response = await self.session.put(upload_url, data=data)
        if upload_response.status != 201:
            # TODO is there any other data that we get?
            raise Exception("Failed to upload file.")

        return MessageAttachmentCreate(
            len(data),
            URN(upload_metadata_response_json.get("urn")),
            media_type,
            filename,
        )

    async def send_message(
        self,
        conversation_urn_or_recipients: Union[URN, List[URN]],
        message_create: MessageCreate,
    ) -> SendMessageResponse:
        params = {"action": "create"}
        message_create_key = "com.linkedin.voyager.messaging.create.MessageCreate"

        message_event: Dict[str, Any] = {
            "eventCreate": {"value": {message_create_key: message_create.to_dict()}}
        }

        if isinstance(conversation_urn_or_recipients, list):
            message_event["recipients"] = [
                r.get_id() for r in conversation_urn_or_recipients
            ]
            message_event["subtype"] = "MEMBER_TO_MEMBER"
            payload = {
                "keyVersion": "LEGACY_INBOX",
                "conversationCreate": message_event,
            }
            res = await self._post(
                "/messaging/conversations",
                params=params,
                json=payload,
            )
        else:
            conversation_id = conversation_urn_or_recipients.get_id()
            res = await self._post(
                f"/messaging/conversations/{conversation_id}/events",
                params=params,
                json=message_event,
            )

        return SendMessageResponse.from_json(await res.text())

    async def download_linkedin_media(self, url: str) -> bytes:
        return await (await self.session.get(url)).content.read()

    # endregion

    # region Profiles

    async def get_user_profile(self) -> UserProfileResponse:
        response = await self._get("/me")
        return UserProfileResponse.from_json(await response.text())

    async def download_profile_picture(self, picture: Picture) -> bytes:
        resp = await self.session.get(
            picture.vector_image.root_url
            + picture.vector_image.artifacts[-1].file_identifying_url_path_segment
        )
        return await resp.content.read()

    # endregion

    # region Event Listener

    def add_event_listener(
        self,
        payload_key: str,
        fn: Callable[[Any], Awaitable[None]],
    ):
        self.event_listeners[payload_key].append(fn)

    object_translation_map: Dict[str, DataClassJsonMixin] = {
        "event": ConversationEvent,
        "reactionSummary": ReactionSummary,
    }

    async def _fire(self, payload_key: str, event: Any):
        for listener in self.event_listeners[payload_key]:
            await listener(event)

    async def _listen_to_event_stream(self):
        logging.info("Starting event stream listener")

        async with self.session.get(
            "https://realtime.www.linkedin.com/realtime/connect",
            headers={"content-type": "text/event-stream", **REQUEST_HEADERS},
            timeout=2 ** 128,
        ) as resp:
            while True:
                chunk = await resp.content.readline()
                if not chunk:
                    break
                if not chunk.startswith(b"data:"):
                    continue
                data = json.loads(chunk.decode("utf-8")[6:])
                event_payload = data.get(
                    "com.linkedin.realtimefrontend.DecoratedEvent", {}
                ).get("payload", {})

                # TODO this should probably pass the entire event_payload to the
                # translation map
                for key, translate_to in self.object_translation_map.items():
                    value = event_payload.get(key)
                    if value is not None:
                        await self._fire(key, translate_to.from_dict(value))

        logging.info("Event stream closed")

    async def start_listener(self):
        try:
            while True:
                await self._listen_to_event_stream()
        except Exception as e:
            logging.exception(f"Error listening to event stream: {e}")

    # endregion
