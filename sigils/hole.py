import random
from datetime import timedelta
import re

from discord.ext import commands
import discord

TIMEOUT_RE = re.compile(r"(computer|boys), \w+ this \w+")


class Hole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, m: discord.Message):
        if TIMEOUT_RE.match(m.content):
            if m.reference is None:
                await m.reply("Ay, whoa whoa whoa, whos am I s'posed to be killings here? Da air?")
                return

            om = m.reference.cached_message
            if om is None:
                om = await m.channel.fetch_message(m.reference.message_id)

            if om.author == m.author:
                await m.reply("https://holedaemon.net/images/snipes.jpg")
                return

            try:
                r = random.randint(0, 60)
                until = discord.utils.utcnow() + timedelta(seconds=r)

                await om.author.timeout(until, reason="Another victim of the Robot Mafia")
            except discord.Forbidden:
                await m.reply("Sorry boss, da feds got in da way")
            else:
                await m.reply("Da jobs dones, boss")


async def setup(bot):
    await bot.add_cog(Hole(bot))
