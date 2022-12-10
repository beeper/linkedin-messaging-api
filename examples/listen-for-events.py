import asyncio
import logging
from pathlib import Path

from linkedin_messaging import ChallengeException, LinkedInMessaging
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
        print("MESSAGE")
        if (e := event.event) and (ec := e.event_content) and (me := ec.message_event):
            print("REDACTION?", me.recalled_at)
        print(event)

    async def on_reaction(event: RealTimeEventStreamEvent):
        print("REACTION")
        print(event)
        assert event.event_urn
        assert event.reaction_summary
        print(await linkedin.get_reactors(event.event_urn, event.reaction_summary.emoji))

    linkedin.add_event_listener("event", on_event)
    linkedin.add_event_listener("reactionSummary", on_reaction)

    task = asyncio.create_task(linkedin.start_listener())

    # wait basically forever
    await asyncio.sleep(2**128)

    asyncio.gather(task)

    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
