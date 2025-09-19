from mcfetch import Player
from discord import Interaction, Embed

from voxlib.api.utils import IntegrationHelper, PlayerInfo
from voxlib.database.utils import Linking
from voxlib import check_if_valid_ign, COLOR_RED, mojang_session


async def link_interaction(
    interaction: Interaction,
    player: str | None
) -> None:
    """
    Handle the `/link` interaction for linking a Discord user to a player UUID.

    Args:
        interaction (Interaction): The Discord interaction context.
        player (str | None): The IGN of the player to link, or None to use integration checks.

    Returns:
        None: Sends a response to the Discord interaction with success or error details.
    """
    try:
        linked_player = Linking(interaction.user.id).get_linked_player()
        if linked_player:
            ign = Player(player=linked_player[1], requests_obj=mojang_session).name
            return await interaction.edit_original_response(
                content=f"You are already linked as **{ign}**. Want to unlink? Run `/unlink`"
            )
        
        uuid = await check_if_valid_ign(interaction, player)
        if not uuid:
            return None
                
        integration = IntegrationHelper()
        get_uuid = await integration.get_player_uuid_from_discord(interaction.user.id)
        get_id = await integration.get_discord_id_from_player(uuid)

        if None in (get_uuid, get_id):
            embed = Embed(
                title="Player Not Integrated To Voxyl Network!", color=COLOR_RED,
                description=(
                    f"To successfully link your account, please ensure that you're using the correct ign and Discord that's integrated to the Voxyl Network.\n\n"
                    f"**Follow the steps below to integrate to the Voxyl Network.**\n"
                    f"- ` 1. ` Join the official Bedwars Practice Discord [here](https://discord.gg/7Mt7T8hqr4).\n"
                    f"- ` 2. ` Go to the following channel https://discord.com/channels/703935026282233946/735838687526518874.\n"
                    f"- ` 3. ` Launch Minecraft and join `sync.voxyl.net`. \n"
                    f"- ` 4. ` Copy the Integration Code shown on screen. *Do NOT share this code!*\n"
                    f"- ` 5. ` Go back to https://discord.com/channels/703935026282233946/735838687526518874\n  - ` 5.1 ` Use `;integrate <ign> <integration-code>`.\n"
                    f"- ` 6. ` You're now integrated to the Voxyl Network.\n"
                    f"- ` 7. ` After the integration run `/link <ign>` again.\n"
                )
            )
            return await interaction.edit_original_response(embed=embed)            
        else:
            name = Player(player=get_uuid, requests_obj=mojang_session).name

            if interaction.user.id == get_id:
                uuid = str(get_uuid).replace('-', '')
                Linking(interaction.user.id).link_player(uuid)
                return await interaction.edit_original_response(
                    content=f"You have successfully linked as **{name}**."
                )
            else:
                return await interaction.edit_original_response(
                    content=f"You are integrated to **{name}**. Run `/link <{name}>` to link your account."
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


async def unlink_interaction(
    interaction: Interaction,        
) -> None:
    """
    Handle the `/unlink` interaction for removing a Discord user's link to a player.

    Args:
        interaction (Interaction): The Discord interaction context.

    Returns:
        None: Sends a response to the Discord interaction with success or error details.
    """
    try:
        linked_player = Linking(interaction.user.id).get_linked_player()
        if not linked_player:
            return await interaction.edit_original_response(
                content=f"You don't have an account linked! Use `/link` to link your account."
            )

        Linking(interaction.user.id).unlink_player()
        await interaction.edit_original_response(
            content=f"You have been successfully unlinked."
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
