import discord
from discord import app_commands


class TARSbot(discord.Client):
    my_guild = None

    def __init__(self, *, intents: discord.Intents, description: str):
        super().__init__(intents=intents, description=description)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if self.my_guild:
            self.tree.copy_global_to(guild=self.my_guild)
            await self.tree.sync(guild=self.my_guild)
