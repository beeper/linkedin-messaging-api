import asyncio
from pathlib import Path

from linkedin_messaging import ChallengeException, LinkedInMessaging
from linkedin_messaging.api_objects import URN

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")
urn = URN("urn:li:fs_conversation:2-YWM2YTJmYjUtNTdjMS00ZjlmLTgwMDUtOWYxMmMxNjY4M2FlXzAxMg==")


async def main():
    linkedin = LinkedInMessaging()
    if cookie_path.exists():
        with open(cookie_path, "rb") as cf:
            linkedin = LinkedInMessaging.from_pickle(cf.read())

    if not await linkedin.logged_in():
        try:
            await linkedin.login("EMAIL", "PASSWORD")
        except ChallengeException:
            await linkedin.enter_2fa(input("2fa code: "))

        with open(cookie_path, "wb+") as cf:
            cf.write(linkedin.to_pickle())

    try:
        # Get a list of all of the conversations for the given user.
        conversations = await linkedin.get_conversations()
        for c in conversations.elements:
            print(c)

        # Get a specific conversation by URN.
        convo_resp = await linkedin.get_conversation(urn)
        for element in convo_resp.elements:
            print(element)

    finally:
        await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
