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
            await linkedin.login("li-1@sumnerevans.com", "oheaqfuy1243")
        except ChallengeException:
            await linkedin.enter_2fa(input("2fa code: "))

        with open(cookie_path, "wb+") as cf:
            cf.write(linkedin.to_pickle())

    # Send a simple message that has some text.
    mc = MessageCreate(AttributedBody("test"))
    message = await linkedin.send_message(urn, mc)

    # Adding reactions
    print(
        await linkedin.add_emoji_reaction(
            message.value.conversation_urn,
            message.value.event_urn,
            "😃",
        )
    )
    print(
        await linkedin.add_emoji_reaction(
            message.value.conversation_urn,
            message.value.event_urn,
            "🤑",
        )
    )

    await asyncio.sleep(5)

    # Remove one of them
    print(
        await linkedin.remove_emoji_reaction(
            message.value.conversation_urn,
            message.value.event_urn,
            "😃",
        )
    )

    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
