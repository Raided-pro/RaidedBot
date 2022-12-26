import discord
from discord.ext import commands
import logging
import json
import asyncio
from RaidedGW2Bot import bot as gw2Bot
from EventManager import bot as eventMan
from typing import Literal


class RaidedBot(commands.Bot):
    def __init__(
        self,
        *args,
        intents: discord.Intents,
        **kwargs,
    ):
        super().__init__(*args, intents=intents, **kwargs)

    async def setup_hook(self):
        serverID = discord.Object(id=826138485743288330)
        self.tree.copy_global_to(guild=serverID)
        await self.tree.sync(guild=serverID)


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self.bot.user}!")

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        options: Literal["unsync", "sync", "global"],
        guild: discord.Guild = discord.Object(id=826138485743288330),
    ):
        if options == "unsync":
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
        elif options == "sync":
            await self.bot.tree.sync(guild=guild)
        elif options == "global":
            await self.bot.tree.sync()
        else:
            await ctx.send("Invalid option", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    async def load_cog(
        self, ctx: commands.Context, cog: Literal["gw2", "event"]
    ):
        if cog == "gw2":
            await ctx.send("GW2 module is not ready yet", ephemeral=True)
        elif cog == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                # Reload extension
                await self.bot.reload_extension("EventManager.bot")
                await ctx.send("Events manager cog reloaded", ephemeral=True)
            else:
                # Load extension
                await self.bot.load_extension("EventManager.bot")
                await ctx.send("Events manager cog loaded", ephemeral=True)
        else:
            await ctx.send("Invalid module", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    async def unload_cog(
        self, ctx: commands.Context, cog: Literal["gw2", "event"]
    ):
        if cog == "gw2":
            await ctx.send("GW2 cog is not ready yet", ephemeral=True)
        elif cog == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                await self.bot.unload_extension("EventManager.bot")
                await ctx.send("Events manager cog unloaded", ephemeral=True)
            else:
                await ctx.send(
                    "Events manager cog is not loaded", ephemeral=True
                )
        else:
            await ctx.send("Invalid module", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    async def list_cogs(self, ctx: commands.Context):
        await ctx.send(
            "Loaded cogs: " + ", ".join(self.bot.extensions.keys()),
            ephemeral=True,
        )


if __name__ == "__main__":
    # Load config
    with open("botDevConfig.json") as f:
        config = json.load(f)

    # Setup logger
    logger = logging.getLogger("discord")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(
        filename="bot.log", encoding="utf-8", mode="a"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = RaidedBot(
        command_prefix="$",
        intents=intents,
        application_id=config["application_id"],
    )

    async def setup(bot):
        await bot.add_cog(General(bot))
        await bot.start(config["token"])

    asyncio.run(setup(bot))
