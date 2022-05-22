import discord
from discord.ext import commands
import logging
import json
import asyncio
from RaidedGW2Bot import bot as gw2Bot
from EventManager import bot as eventMan


class RaidedBot(commands.Bot):
    def __init__(
        self,
        *args,
        intents: discord.Intents,
        **kwargs,
    ):
        super().__init__(*args, intents=intents, **kwargs)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        serverID = discord.Object(id=940689261567557634)
        self.tree.copy_global_to(guild=serverID)
        await self.tree.sync(guild=serverID)

        
class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self.bot.user}!")

if __name__ == "__main__":
    # Load config
    with open("botConfig.json") as f:
        config = json.load(f)

    # Setup logger
    logger = logging.getLogger("discord")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(
        filename="bot.log", encoding="utf-8", mode="w"
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
        await bot.add_cog(gw2Bot.LogUploader(bot, gw2Bot.gw2.app.teamIDs))
        await bot.add_cog(eventMan.EventManager(bot))
        await bot.start(config["token"])

    asyncio.run(setup(bot))
