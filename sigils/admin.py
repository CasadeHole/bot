from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands


if TYPE_CHECKING:
    from bot import DONG


class Admin(commands.Cog):
    """Admin-only commands."""

    def __init__(self, bot: DONG):
        self.bot: DONG = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, ext: str):
        """Reload a extension."""
        try:
            await self.bot.reload_extension(ext)
        except commands.ExtensionError as e:
            await ctx.reply(f"Error reloading extension: {e}")
        else:
            await ctx.reply("\N{OK HAND SIGN}")


async def setup(bot: DONG):
    await bot.add_cog(Admin(bot))
