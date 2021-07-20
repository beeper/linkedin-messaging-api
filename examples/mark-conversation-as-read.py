from pathlib import Path

import asyncio
from linkedin_messaging import ChallengeException, LinkedInMessaging
from linkedin_messaging.api_objects import URN

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")
urn = URN("2-YWM2YTJmYjUtNTdjMS00ZjlmLTgwMDUtOWYxMmMxNjY4M2FlXzAxMg==")


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
        print(await linkedin.mark_conversation_as_read(urn))
    finally:
        await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
