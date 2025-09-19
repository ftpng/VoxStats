from discord.ext import commands
from discord import app_commands, Interaction

from voxlib import link_interaction, unlink_interaction


class Linking(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @app_commands.command(name="link", description="Link your account")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(player="The player you want to link to")
    async def link(
        self, interaction: Interaction, player: str, 
    ):
        await interaction.response.defer()
        await link_interaction(interaction, player)


    @app_commands.command(name="unlink", description="Unlink your account")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def unlink(
        self, interaction: Interaction
    ):
        await interaction.response.defer()
        await unlink_interaction(interaction)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Linking(client))