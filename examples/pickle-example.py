import asyncio
from pathlib import Path

from linkedin_messaging import ChallengeException, LinkedInMessaging

cookie_path = Path(__file__).parent.joinpath("cookies.pickle")


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

    print(await linkedin.get_user_profile())

    await linkedin.logout()
    await linkedin.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
