import os
import asyncio
import logging

from tortoise import Tortoise
from bot import DONG


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def main():
    token = os.getenv("DONG_TOKEN")
    if token is None:
        log.fatal("$DONG_TOKEN was not specified")
        return

    dsn = os.getenv("DONG_DSN")
    if dsn is None:
        log.fatal("$DONG_DSN was not specified")
        return

    await Tortoise.init(
        db_url=dsn,
        modules={"models": ["sigils.utils.db"]}
    )
    await Tortoise.generate_schemas()

    b = DONG()

    async with b:
        await b.start(token)

if __name__ == "__main__":
    asyncio.run(main())
