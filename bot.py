import logging

import discord
from discord.ext import commands


HOLEDAEMON_BASE = "https://holedaemon.net/images"

log = logging.getLogger(__name__)
initial_sigils = (
    "sigils.admin",
    "sigils.hole",
    # "sigils.quote",
)


class DONG(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=discord.Intents().all(),
        )

    def asset(self, title: str, ext: str = None) -> str:
        return f"{HOLEDAEMON_BASE}/{title}.{ext if ext is not None else '.jpg'}"

    async def setup_hook(self):
        try:
            for sigil in initial_sigils:
                await self.load_extension(sigil)
        except commands.ExtensionError as e:
            log.error(f"error loading extension: {e}")

    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        await self.process_commands(msg)
