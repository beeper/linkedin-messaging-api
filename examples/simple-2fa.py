from pathlib import Path

import asyncio
from linkedin_messaging import LinkedInMessaging, ChallengeException

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")


async def main():
    linkedin = LinkedInMessaging()

    try:
        await linkedin.login("EMAIL", "PASSWORD")
    except ChallengeException:
        await linkedin.enter_2fa(input("2fa code: "))

    print(await linkedin.get_user_profile())

    await linkedin.close()


loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
loop.close()
