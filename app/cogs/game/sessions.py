from discord.ext import commands
from discord import app_commands, Interaction, File
from datetime import datetime

from voxlib.rendering import render_session
from voxlib.database.utils import Sessions
from voxlib import (
    check_if_linked_discord, 
    fetch_player,
    DIR
)


class Session(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    session = app_commands.Group(
        name='session',
        description='View and manage active sessions',
        allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
    )


    @session.command(name="start", description="Starts a new session")
    @app_commands.describe(session="The session you want to start")
    @app_commands.choices(session=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="2", value=2),
        app_commands.Choice(name="3", value=3),
    ])
    async def start_session(self, interaction: Interaction, session: int):
        try:
            await interaction.response.defer()
            if not (uuid := await check_if_linked_discord(
                interaction, 'You must have an account linked to use this command.')
            ):
                return None

            session_stats = Sessions(uuid, session).get_session()
            if session_stats:
                return await interaction.edit_original_response(
                    content=f'This session is already active, if you want to end this session run the `/session end` command.'
                )
            
            try:
                await Sessions(uuid, session).create_session()
                return await interaction.edit_original_response(
                    content=f'A new session was successfully created with Session ID: **{session}**.'
                )
            except Exception as error:
                print(error)

        except Exception as error:
            print(error)
            await interaction.edit_original_response(
                content=(
                    "Something went wrong. If this issue persists, please contact "
                    "the **VoxStats Dev Team.** for more information."
                )
            )
            return None


    @session.command(name="end", description="Ends a session")
    @app_commands.describe(session="The session you want to end")
    @app_commands.choices(session=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="2", value=2),
        app_commands.Choice(name="3", value=3),
    ])
    async def end_session(self, interaction: Interaction, session: int):
        try:
            await interaction.response.defer()
            if not (uuid := await check_if_linked_discord(
                interaction, 'You must have an account linked to use this command.')
            ):
                return None

            session_stats = Sessions(uuid, session).get_session()
            if session_stats:
                Sessions(uuid, session).end_session()
                return await interaction.edit_original_response(
                    content=f'Session **{session}** has been deleted successfully.'
                )
            else:
                return await interaction.edit_original_response(
                    content=f"You don't have an active session with session ID: **{session}**."
                )                

        except Exception as error:
            print(error)
            await interaction.edit_original_response(
                content=(
                    "Something went wrong. If this issue persists, please contact "
                    "the **VoxStats Dev Team.** for more information."
                )
            )
            return None


    @session.command(name="reset",description="Resets a session")
    @app_commands.describe(session="The session you want to reset")
    @app_commands.choices(session=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="2", value=2),
        app_commands.Choice(name="3", value=3),
    ])
    async def reset_session(self, interaction: Interaction, session: int):
        try:
            await interaction.response.defer()
            if not (uuid := await check_if_linked_discord(
                interaction, 'You must have an account linked to use this command.')
            ):
                return None      

            session_stats = Sessions(uuid, session).get_session()
            if session_stats:
                await Sessions(uuid, session).reset_session()
                return await interaction.edit_original_response(
                    content=f'Session **{session}** has been reset successfully.'
                ) 
            else:
                return await interaction.edit_original_response(
                    content=f"You don't have an active session with session ID: **{session}**."
                )
            
        except Exception as error:
            print(error)
            await interaction.edit_original_response(
                content=(
                    "Something went wrong. If this issue persists, please contact "
                    "the **VoxStats Dev Team.** for more information."
                )
            )
            return None
         

    @session.command(name="active", description="View the active sessions")
    async def active_sessions(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            if not (uuid := await check_if_linked_discord(
                interaction, 'You must have an account linked to use this command.')
            ):
                return None             

            active_sessions = Sessions(uuid).get_active_sessions()
            if active_sessions:
                sessions = ", ".join(str(item[0]) for item in sorted(active_sessions))
                return await interaction.edit_original_response(
                    content=f"Your active sessions: **{sessions}**"
                )
            else:
                return await interaction.edit_original_response(
                    content=f"You don't have any sessions active! Use `/session start` to create one."
                )                

        except Exception as error:
            print(error)
            await interaction.edit_original_response(
                content=(
                    "Something went wrong. If this issue persists, please contact "
                    "the **VoxStats Dev Team.** for more information."
                )
            )
            return None


    @session.command(name="view", description="View the session of a player")
    @app_commands.describe(
        player="The player you want to view",
        session="The session you want to view (default 1)"
    )
    @app_commands.choices(session=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="2", value=2),
        app_commands.Choice(name="3", value=3),
    ])
    async def view_session(self, interaction: Interaction, player: str = None, session: int = 1):
        try:
            await interaction.response.defer()

            if not (uuid := await fetch_player(interaction, player)):
                return None
            
            sessions = Sessions(uuid, session).get_session()
            if not sessions:
                await Sessions(uuid, session).create_session()
                return await interaction.edit_original_response(
                    content=
                        f"This player has no active session with session ID: **{session}**\n"
                        f"I have created a new session for this player with session ID: **{session}**"
                )   
            if session:
                await render_session(uuid, session)
                await interaction.edit_original_response(
                    attachments=[File(f"{DIR}assets/stats/session.png")]
                )
            else:
                return await interaction.edit_original_response(
                    content=f"You don't have an active session with ID: **{session}**"
                )                

        except Exception as error:
            print(error)
            await interaction.edit_original_response(
                content=(
                    "Something went wrong. If this issue persists, please contact "
                    "the **VoxStats Dev Team.** for more information."
                )
            )
            return None

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Session(client))