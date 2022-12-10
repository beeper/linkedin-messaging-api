import asyncio

from linkedin_messaging import LinkedInMessaging
from linkedin_messaging.api_objects import URN

urn = URN("urn:li:fs_conversation:2-YWM2YTJmYjUtNTdjMS00ZjlmLTgwMDUtOWYxMmMxNjY4M2FlXzAxMg==")


async def main():
    linkedin = LinkedInMessaging()
    await linkedin.login_manual(
        "FOO",
        "ajax:1234567890",
    )

    assert await linkedin.logged_in()

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
