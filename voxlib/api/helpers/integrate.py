from voxlib.api import API, VoxylApiEndpoint


class IntegrationHelper:
    """
    Helper class for interacting with the Voxyl API integration endpoints.
    """
    @staticmethod
    async def get_discord_id_from_player(uuid: str) -> str | None:
        """
        Fetch the linked Discord account ID for a given player.

        Args:
            uuid (str): The UUID of the player.

        Returns:
            str | None: The Discord account ID if available, otherwise None.
        """
        data: dict = await API.make_request(
            VoxylApiEndpoint.DISCORD_FROM_PLAYER,
            uuid=uuid
        )
        return data.get('id') if data else None

    @staticmethod
    async def get_player_uuid_from_discord(discord_id: str) -> str | None:
        """
        Fetch the linked player UUID for a given Discord account.

        Args:
            discord_id (str): The ID of the Discord account.

        Returns:
            str | None: The player UUID if available, otherwise None.
        """
        data: dict = await API.make_request(
            VoxylApiEndpoint.PLAYER_FROM_DISCORD,
            discord_id=discord_id
        )
        return data.get('uuid') if data else None
