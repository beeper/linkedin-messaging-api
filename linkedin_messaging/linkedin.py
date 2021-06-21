import json
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .api_objects import ConversationsResponse, ConversationResponse, URN

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

    def __init__(self):
        self.session = aiohttp.ClientSession()

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

    # region Authentication

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
            cookie_names = {c.key for c in self.session.cookie_jar}
            if (
                "liap" in cookie_names
                and "li_at" in cookie_names
                and "JSESSIONID" in cookie_names
            ):
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
            cookie_names = {c.key for c in self.session.cookie_jar}
            if (
                "liap" in cookie_names
                and "li_at" in cookie_names
                and "JSESSIONID" in cookie_names
            ):
                for c in self.session.cookie_jar:
                    if c.key == "JSESSIONID":
                        self.session.headers["csrf-token"] = c.value.strip('"')
                return
            # TODO can we scrape anything from the page?
            raise Exception("Failed to log in.")

    # endregion

    async def get_conversations(
        self,
        last_activity_before: Optional[datetime] = None,
    ) -> ConversationsResponse:
        """
        Fetch list of conversations the user is in.

        :param last_activity_before: datetime of the last chat activity to consider
        :type last_activity_before: datetime?

        :return: List of conversations
        :rtype: list
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
        Fetch data about a given conversation.

        :param conversation_urn_id: LinkedIn URN ID for a conversation
        :type conversation_urn_id: str

        :param created_before: datetime of the last chat activity to consider
        :type created_before: datetime?

        :return: Conversation data
        :rtype: dict
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
