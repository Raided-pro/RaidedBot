import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import asyncio
from typing import Literal

DEBUGGUILD = 826138485743288330


class RaidedBot(commands.Bot):
    def __init__(
        self,
        *args,
        intents: discord.Intents,
        **kwargs,
    ):
        super().__init__(*args, intents=intents, **kwargs)

    async def setup_hook(self):
        serverID = discord.Object(id=DEBUGGUILD)
        self.tree.copy_global_to(guild=serverID)
        await self.tree.sync(guild=serverID)

        # Load cogs on startup
        await self.load_extension("EventManager.bot")


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self.bot.user}!")

    @app_commands.default_permissions(administrator=True)
    class ModuleGroup(app_commands.Group):
        def __init__(self):
            super().__init__(name="module", description="Manage modules")

    moduleGroup = ModuleGroup()

    @moduleGroup.command(description="Load a module's commands")
    async def load(
        self, interaction: discord.Interaction, module: Literal["gw2", "event"]
    ):
        if module == "gw2":
            await interaction.response.send_message(
                content="GW2 module is not ready yet.", ephemeral=True
            )
        elif module == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                # Defer as this might take a bit
                await interaction.response.defer(ephemeral=True, thinking=True)

                # Reload extension
                commandCount = await self._add_module_commands(
                    self.bot.cogs["EventManager"], interaction.guild
                )

                await interaction.followup.send(
                    content=f"Events manager module reloaded with {commandCount} command(s).",
                )
            else:
                # Extension not available
                await interaction.response.send_message(
                    content="Events manager cog is unavailable.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                content="Invalid module", ephemeral=True
            )

    @moduleGroup.command(description="Unload a module's commands")
    async def unload(
        self, interaction: discord.Interaction, module: Literal["gw2", "event"]
    ):
        if module == "gw2":
            await interaction.response.send_message(
                content="GW2 module is not ready yet.", ephemeral=True
            )
        elif module == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                # Defer as this might take a bit
                await interaction.response.defer(ephemeral=True, thinking=True)

                commandCount = await self._remove_module_commands(
                    self.bot.cogs["EventManager"], interaction.guild
                )
                await interaction.followup.send(
                    content=f"Events manager module unloaded with {commandCount} command(s).",
                )
            else:
                await interaction.response.send_message(
                    content="Events manager cog is not loaded", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                content="Invalid module", ephemeral=True
            )

    async def _add_module_commands(self, cog, guild):
        counter = 0
        for command in cog.walk_app_commands():
            self.bot.tree.add_command(command, guild=guild, override=True)
            counter += 1

        await self.bot.tree.sync(guild=guild)

        return counter

    async def _remove_module_commands(self, cog, guild):
        counter = 0
        for command in cog.walk_app_commands():
            removed = self.bot.tree.remove_command(command.name, guild=guild)
            if removed is not None:
                counter += 1

        await self.bot.tree.sync(guild=guild)
        return counter

    @app_commands.guilds(DEBUGGUILD)
    class DevGroup(app_commands.Group):
        def __init__(self):
            super().__init__(name="dev", description="Development commands")

    devGroup = DevGroup()

    @devGroup.command(description="Load a cog")
    @commands.is_owner()
    async def load_cog(
        self, interaction: discord.Interaction, cog: Literal["gw2", "event"]
    ):
        if cog == "gw2":
            await interaction.response.send_message(
                content="GW2 module is not ready yet", ephemeral=True
            )
        elif cog == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                # Reload extension
                await self.bot.reload_extension("EventManager.bot")
                await interaction.response.send_message(
                    content="Events manager cog reloaded", ephemeral=True
                )
            else:
                # Load extension
                await self.bot.load_extension("EventManager.bot")
                await interaction.response.send_message(
                    content="Events manager cog loaded", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                content="Invalid module", ephemeral=True
            )

    @devGroup.command(description="Unload a cog")
    @commands.is_owner()
    async def unload_cog(
        self, interaction: discord.Interaction, cog: Literal["gw2", "event"]
    ):
        if cog == "gw2":
            await interaction.response.send_message(
                content="GW2 cog is not ready yet", ephemeral=True
            )
        elif cog == "event":
            # Check if the events manager cog is loaded
            if "EventManager.bot" in self.bot.extensions:
                await self.bot.unload_extension("EventManager.bot")
                await interaction.response.send_message(
                    content="Events manager cog unloaded", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    content="Events manager cog is not loaded", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                content="Invalid module", ephemeral=True
            )

    @devGroup.command(description="List loaded cogs")
    @commands.is_owner()
    async def list_cogs(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Loaded cogs: " + ", ".join(self.bot.extensions.keys()),
            ephemeral=True,
        )

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!", ephemeral=True)

    @commands.command()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        options: Literal["unsync", "sync", "global"],
        guild: discord.Guild = discord.Object(id=DEBUGGUILD),
    ):
        if options == "unsync":
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
            await ctx.send("Commands unsynced", ephemeral=True)
        elif options == "sync":
            await self.bot.tree.sync(guild=guild)
            await ctx.send("Commands synced", ephemeral=True)
        elif options == "global":
            await self.bot.tree.sync()
            await ctx.send("Commands synced globally", ephemeral=True)
        else:
            await ctx.send("Invalid option", ephemeral=True)


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
