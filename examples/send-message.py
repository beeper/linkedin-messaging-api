import asyncio
import logging
from pathlib import Path

from linkedin_messaging import ChallengeException, LinkedInMessaging
from linkedin_messaging.api_objects import URN, AttributedBody, MessageCreate

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")
urn = URN("urn:li:fs_conversation:2-OTNkODIyYTEtODFjZS00NTdlLThlYTItYWQyMDg2NTc4YWMyXzAxMA==")


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
    print(await linkedin.send_message(urn, mc))

    # Send a multimedia message.
    with open("/path/to/the/cool-pic.jpg", "rb") as f:
        attachment = await linkedin.upload_media(f.read(), "cool-pic.jpg", "image/jpeg")

    mc = MessageCreate(AttributedBody(), attachments=[attachment])
    print(await linkedin.send_message(urn, mc))

    await linkedin.logout()
    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
