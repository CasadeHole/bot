import logging

from tortoise.functions import Max
from tortoise.exceptions import OperationalError
import discord
from discord.ext import commands

from .utils.db import Quote as Q


log = logging.getLogger(__name__)


class Quote(commands.Cog):
    """Functionality related to quotes."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.is_custom_emoji():
            return

        if payload.emoji.name == "\N{SPEECH BALLOON}":
            exists = await Q().exists(message_id=str(payload.message_id))
            if exists:
                return

            g = self.bot.get_guild(payload.guild_id)
            member = payload.member
            if payload.member is None:
                member = g.get_member(payload.user_id)
            
            if member is None:
                return

            if member == self.bot.user:
                return

            ch = self.bot.get_channel(payload.channel_id)
            try:
                msg = await ch.fetch_message(payload.message_id)
            except discord.NotFound:
                return
            except discord.Forbidden as e:
                log.error(f"error getting message: forbidden: {e}")
                return

            if msg.content == "":
                return

            q = await Q.filter(guild_id=str(payload.guild_id)).first().annotate(count=Max("num")).values("count")
            num = 1
            if q["count"] is not None:
                num = q["count"] + 1

            try:
                await Q.create(
                    message_id=str(payload.message_id),
                    guild_id=str(payload.guild_id),
                    channel_id=str(payload.channel_id),
                    author_id=str(payload.user_id),
                    content=msg.content,
                    num=num,
                )
            except OperationalError as e:
                log.error(f"error inserting quote: {e}")
            else:
                await ch.send(f"New quote added by {member.name}. This is quote #{num}. {msg.jump_url}")

    @commands.group(aliases=["q"])
    async def quote(self, ctx: commands.Context):
        """Group for interacting with quotes."""
        return

    @quote.command(aliases=["delete"])
    async def remove(self, ctx: commands.Context, quote: int):
        """Remove a quote."""
        q = await Q.get_or_none(guild_id=str(ctx.guild.id), num=quote)
        if q is None:
            return await ctx.reply("Quote doesn't exist, nerd")

        try:
            await q.delete()
        except OperationalError as e:
            log.error(f"error removing quote: {e}")
            return await ctx.reply(
                "Sorry, something to do with the database broke, and I wasn't able to remove the quote."
            )
        else:
            return await ctx.reply("Quote removed.")


async def setup(bot):
    await bot.add_cog(Quote(bot))
