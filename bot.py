import discord
from discord.ext import commands
import logging
import json
import RaidedGW2Bot.bot as gw2Bot


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

    bot = commands.Bot(command_prefix="$", intents=intents)
    bot.add_cog(General(bot))
    bot.add_cog(gw2Bot.LogUploader(bot, gw2Bot.gw2.teamIDs))
    bot.run(config["token"])
