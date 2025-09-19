from typing import Optional
from discord import Interaction
from mcfetch import Player

from voxlib.database.utils import Linking
from voxlib.api.utils import PlayerInfo
from voxlib import mojang_session


async def check_if_ever_played(
    interaction: Interaction,
    uuid: str
) -> bool:
    """
    Check if a player with the given UUID has ever played on the server.

    Args:
        interaction (Interaction): The Discord interaction context.
        uuid (str): The UUID of the player.

    Returns:
        bool: True if the player has played before, False if not.
              Returns None if no UUID was provided.
    """
    if not uuid:
        return None

    player = PlayerInfo(uuid)
    last_login = await player.last_login_time

    if last_login is None:
        await interaction.edit_original_response(
            content='This player has never played on `bedwarspractice.club` before!'
        )
        return False

    return True


async def check_if_linked(
    interaction: Interaction,
    player: Optional[str]
) -> Optional[str]:
    """
    Ensure a player name is provided, falling back to the linked account if available.

    Args:
        interaction (Interaction): The Discord interaction context.
        player (Optional[str]): The player's IGN if provided.

    Returns:
        Optional[str]: The resolved player name, or None if no linked account exists
                       and no player was provided.
    """
    if player is None:
        linked = Linking(interaction.user.id).get_linked_player()

        if linked:
            player = Player(player=linked[1], requests_obj=mojang_session).name

        if not player:
            await interaction.edit_original_response(
                content="You are not linked! Either specify a player or link your account using `/link`"
            )
            return None

    return player


async def check_if_linked_discord(
    interaction: Interaction,
    message: str = None
) -> Optional[str]:
    """
    Ensure the Discord user has a linked account.

    Args:
        interaction (Interaction): The Discord interaction context.
        message (str, optional): Custom error message if not linked.
            Defaults to a generic message.

    Returns:
        Optional[str]: The linked player UUID if available, otherwise None.
    """
    if not message:
        message = "You are not linked! Either specify a player or link your account using `/link`"

    linked = Linking(interaction.user.id).get_linked_player()
    if not linked:
        await interaction.edit_original_response(content=message)
        return None

    return linked[1]


async def not_exist_message(interaction: Interaction, player: str):
    """
    Sends an error message when a given player does not exist.

    Args:
        interaction (Interaction): The Discord interaction to edit.
        player (str): The username or player identifier that was not found.

    Returns:
        None: The function only edits the interaction response and does not return a value.
    """
    await interaction.edit_original_response(
        content=f"**{player}** does not exist! Please provide a valid username."
    )
    return None


async def check_if_valid_ign(
    interaction: Interaction,
    player: str
) -> Optional[str]:
    """
    Validate that a given player IGN exists and resolve it to a UUID.

    Args:
        interaction (Interaction): The Discord interaction context.
        player (str): The player's in-game name (IGN).

    Returns:
        Optional[str]: The player's UUID if valid, otherwise None.
    """
    if len(player) > 16:
        return await not_exist_message(interaction, player)

    uuid = Player(player=player, requests_obj=mojang_session).uuid

    if uuid is None:
        return await not_exist_message(interaction, player)

    return uuid


async def fetch_player(
    interaction: Interaction,
    player: Optional[str]
) -> Optional[str]:
    """
    Resolve and validate a player's UUID from either a provided IGN
    or a linked account. Ensures the player exists and has played before.

    Args:
        interaction (Interaction): The Discord interaction context.
        player (Optional[str]): The player's IGN if provided, or None to use linked account.

    Returns:
        Optional[str]: The player's UUID if successfully resolved, otherwise None.
    """
    try:
        if not (player := await check_if_linked(interaction, player)):
            return None
        if not (uuid := await check_if_valid_ign(interaction, player)):
            return None
        if not await check_if_ever_played(interaction, uuid):
            return None

        return uuid

    except Exception as error:
        print(error)
        await interaction.edit_original_response(
            content=(
                "The API is currently down. If this issue persists, please contact "
                "the **VoxStats Dev Team.** for more information."
            )
        )
        return None
