from typing import TYPE_CHECKING
import logging

from tortoise.functions import Max
from tortoise.exceptions import OperationalError
from tortoise.contrib.postgres.functions import Random
import discord
from discord.ext import commands

from .utils.db import Quote as Q

if TYPE_CHECKING:
    from bot import DONG


log = logging.getLogger(__name__)


class Quote(commands.Cog):
    """Functionality related to quotes."""

    def __init__(self, bot: DONG):
        self.bot: DONG = bot

    def make_embed(self, q: Q, m: discord.Member) -> discord.Embed:
        e = discord.Embed(
            title=f"#{q.num}",
            color=0x202225,
            timestamp=q.created_at,
        )

        e.add_field(
            name=q.content,
            value=f"[Jump](https://discord.com/channels/{q.guild_id}/{q.channel_id}/{q.message_id})"
        )

        if m is not None:
            e.set_author(name=f"{m.name}#{m.discriminator}", icon_url=m.avatar)

        return e

    async def send_random(self, ctx: commands.Context):
        q = await Q.filter(guild_id=str(ctx.guild.id)).annotate(order=Random()).order_by("order").first()
        if q is None:
            return await ctx.reply("There aren't any quotes, doofus")

        member = ctx.guild.get_member(q.author_id)
        if member is None:
            member = await ctx.guild.fetch_member(q.author_id)

        e = self.make_embed(q, member)
        return await ctx.send(embed=e)

    async def send_random_from_user(self, ctx: commands.Context, uid: str):
        q = await Q.filter(guild_id=str(ctx.guild.id), author_id=uid).annotate(order=Random()).order_by("order").first()
        if q is None:
            return await ctx.reply("There aren't any quotes, doofus")

        member = ctx.guild.get_member(q.author_id)
        if member is None:
            member = await ctx.guild.fetch_member(q.author_id)

        e = self.make_embed(q, member)
        return await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        q = await Q.get_or_none(guild_id=str(payload.guild_id), message_id=str(payload.message_id))
        if q is None:
            return

        g = self.bot.get_channel(payload.channel_id)
        msg = await g.fetch_message(payload.message_id)

        await q.update_from_dict({
            "content": msg.content
        })

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
                    author_id=str(msg.author.id),
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
        if ctx.invoked_subcommand is None:
            clean_content = ctx.message.content.replace(
                ctx.prefix+ctx.invoked_with,
                "",
            ).lstrip()

            if clean_content == "":
                return await self.send_random(ctx)

            if clean_content.isnumeric():
                q = await Q.get_or_none(guild_id=str(ctx.guild.id), num=int(clean_content))
                if q is not None:
                    member = ctx.guild.get_member(q.author_id)
                    if member is None:
                        member = await ctx.guild.fetch_member(q.author_id)

                    e = self.make_embed(q, member)
                    return await ctx.send(embed=e)

            mc = commands.MemberConverter()
            try:
                member = await mc.convert(ctx, clean_content)
            except commands.MemberNotFound:
                pass
            else:
                return await self.send_random_from_user(ctx, member.id)

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
                "Sorry, something to do with the database broke, and I wasn't able to remove the quote"
            )
        else:
            return await ctx.reply("Quote removed.")

    @quote.command()
    async def count(self, ctx: commands.Context):
        """Count the number of quotes in the guild."""
        count = await Q.filter(guild_id=str(ctx.guild.id)).count()
        if count == 0:
            return await ctx.reply("There aren't any quotes")

        if count == 1:
            return await ctx.reply("There is 1 quote")

        return await ctx.reply(f"There are currently {count} quotes")


async def setup(bot: DONG):
    await bot.add_cog(Quote(bot))
