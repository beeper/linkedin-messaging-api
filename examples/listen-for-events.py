import logging
from pathlib import Path

import asyncio
from linkedin_messaging import LinkedInMessaging, ChallengeException
from linkedin_messaging.api_objects import RealTimeEventStreamEvent

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")


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

    async def on_event(event: RealTimeEventStreamEvent):
        print(event)

    linkedin.add_event_listener("event", on_event)
    linkedin.add_event_listener("reactionSummary", on_event)
    linkedin.add_event_listener("reactionAdded", on_event)

    task = asyncio.create_task(linkedin.start_listener())

    # wait basically forever
    await asyncio.sleep(2 ** 128)

    asyncio.gather(task)

    await linkedin.logout()
    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
