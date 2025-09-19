from typing import Any

from voxlib.api import API, VoxylApiEndpoint


class GuildInfo:
    """
    Helper class for fetching and accessing guild-related data
    from the Voxyl Network API.
    """

    def __init__(self, tag_or_id: str):
        """
        Initialize a GuildInfo instance for a specific guild.

        Args:
            tag_or_id (str): The tag of the guild, or `-id` followed by the guild ID.
        """
        self._tag_or_id: str = tag_or_id

    async def fetch_guild_info(self) -> dict | None:
        """
        Fetch the basic information about a guild.

        Returns:
            dict | None: Guild info JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.GUILD_INFO,
            tag_or_id=self._tag_or_id
        )
        return data if data else None

    async def fetch_guild_members(self) -> dict | None:
        """
        Fetch the list of members in the guild.

        Returns:
            dict | None: Guild members JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.GUILD_MEMBERS,
            tag_or_id=self._tag_or_id
        )
        return data if data else None

    @staticmethod
    async def fetch_top_guilds(num: int = 10) -> dict | None:
        """
        Fetch the top guilds by XP.

        Args:
            num (int, optional): Number of guilds to return (maximum 100). Defaults to 10.

        Returns:
            dict | None: Top guilds JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.GUILD_TOP,
            num=num
        )
        return data if data else None

    @property
    async def id(self) -> str | None:
        """
        Get the guild's internal ID.

        Returns:
            str | None: Guild ID, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("id") if guild else None

    @property
    async def name(self) -> str | None:
        """
        Get the guild's name.

        Returns:
            str | None: Guild name, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("name") if guild else None

    @property
    async def description(self) -> str | None:
        """
        Get the guild's description.

        Returns:
            str | None: Guild description, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("desc") if guild else None

    @property
    async def xp(self) -> int | None:
        """
        Get the guild's total XP.

        Returns:
            int | None: Guild XP, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("xp") if guild else None

    @property
    async def member_count(self) -> int | None:
        """
        Get the number of members in the guild.

        Returns:
            int | None: Member count, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("num") if guild else None

    @property
    async def owner_uuid(self) -> str | None:
        """
        Get the UUID of the guild's owner.

        Returns:
            str | None: Owner UUID, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("ownerUUID") if guild else None

    @property
    async def creation_time(self) -> int | None:
        """
        Get the UNIX timestamp when the guild was created.

        Returns:
            int | None: Creation time, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get("time") if guild else None

    @property
    async def members(self) -> list[dict[str, Any]] | None:
        """
        Get the list of guild members.

        Returns:
            list[dict[str, Any]] | None: List of members with role, UUID, and join time,
            or None if unavailable.
        """
        members = await self.fetch_guild_members()
        return members.get("members") if members else None
