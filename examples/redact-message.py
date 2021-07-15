import logging
from pathlib import Path

import asyncio
from linkedin_messaging import LinkedInMessaging, ChallengeException
from linkedin_messaging.api_objects import URN, MessageCreate, AttributedBody

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")
urn = URN("2-YWM2YTJmYjUtNTdjMS00ZjlmLTgwMDUtOWYxMmMxNjY4M2FlXzAxMg==")


async def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

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

    # Send a simple message that has some text.
    mc = MessageCreate(AttributedBody("test"))
    message = await linkedin.send_message(urn, mc)

    await asyncio.sleep(5)

    # Now, delete it
    print(
        await linkedin.delete_message(
            message.value.conversation_urn,
            message.value.event_urn,
        )
    )
    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
