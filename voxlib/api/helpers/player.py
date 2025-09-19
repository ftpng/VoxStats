from typing import Any

from voxlib.api import API, VoxylApiEndpoint


class PlayerInfo:
    """
    Helper class for fetching and accessing player-related data
    from the Voxyl Network API.
    """
    def __init__(self, uuid: str):
        """
        Initialize a PlayerInfo instance for a specific player.

        Args:
            uuid (str): The UUID of the player.
        """
        self._uuid: str = uuid

    async def fetch_player_info(self) -> dict | None:
        """
        Fetch the basic player information.

        Returns:
            dict | None: Player info JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.PLAYER_INFO,
            uuid=self._uuid
        )
        return data if data else None

    async def fetch_overall_stats(self) -> dict | None:
        """
        Fetch the player's overall statistics.

        Returns:
            dict | None: Overall stats JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.PLAYER_OVERALL,
            uuid=self._uuid
        )
        return data if data else None

    async def fetch_game_stats(self) -> dict | None:
        """
        Fetch the player's game-specific statistics.

        Returns:
            dict | None: Game stats JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.PLAYER_STATS,
            uuid=self._uuid
        )
        return data if data else None

    async def fetch_guild_info(self) -> dict | None:
        """
        Fetch the player's guild information.

        Returns:
            dict | None: Guild info JSON response, or None if not available.
        """
        data = await API.make_request(
            VoxylApiEndpoint.PLAYER_GUILD,
            uuid=self._uuid
        )
        return data if data else None

    @property
    async def last_login_name(self) -> str | None:
        """
        Get the last known username of the player.

        Returns:
            str | None: Last login name, or None if unavailable.
        """
        info = await self.fetch_player_info()
        return info.get('lastLoginName') if info else None

    @property
    async def last_login_time(self) -> int | None:
        """
        Get the last login time of the player.

        Returns:
            int | None: UNIX timestamp in seconds, or None if unavailable.
        """
        info = await self.fetch_player_info()
        return info.get('lastLoginTime') if info else None

    @property
    async def role(self) -> str | None:
        """
        Get the player's current role or rank.

        Returns:
            str | None: Role string, or None if unavailable.
        """
        info = await self.fetch_player_info()
        return info.get('role') if info else None


    @property
    async def level(self) -> int | None:
        """
        Get the player's level.

        Returns:
            int | None: Player level, or None if unavailable.
        """
        stats = await self.fetch_overall_stats()
        return stats.get('level') if stats else None

    @property
    async def exp(self) -> int | None:
        """
        Get the player's experience points for their current level.

        Returns:
            int | None: Experience points, or None if unavailable.
        """
        stats = await self.fetch_overall_stats()
        return stats.get('exp') if stats else None

    @property
    async def weightedwins(self) -> int | None:
        """
        Get the player's total weighted wins.

        Returns:
            int | None: Weighted wins, or None if unavailable.
        """
        stats = await self.fetch_overall_stats()
        return stats.get('weightedwins') if stats else None

    @property
    async def stats(self) -> dict | None:
        """
        Get the raw game stats data.

        Returns:
            dict | None: Dictionary of game stats keyed by game type,
            or None if unavailable.
        """
        game_stats = await self.fetch_game_stats()
        return game_stats.get('stats') if game_stats else None

    @property
    async def kills(self) -> int | None:
        """
        Get the total kills across all games.

        Returns:
            int | None: Sum of kills, or None if unavailable.
        """
        game = await self.fetch_game_stats()
        if not game or 'stats' not in game:
            return None

        stats: dict[str, dict[str, Any]] = game['stats']
        return sum(s.get('kills', 0) for s in stats.values())

    @property
    async def wins(self) -> int | None:
        """
        Get the total wins across all games.

        Returns:
            int | None: Sum of wins, or None if unavailable.
        """
        game = await self.fetch_game_stats()
        if not game or 'stats' not in game:
            return None

        stats: dict[str, dict[str, Any]] = game['stats']
        return sum(s.get('wins', 0) for s in stats.values())

    @property
    async def finals(self) -> int | None:
        """
        Get the total final kills across all games.

        Returns:
            int | None: Sum of final kills, or None if unavailable.
        """
        game = await self.fetch_game_stats()
        if not game or 'stats' not in game:
            return None

        stats: dict[str, dict[str, Any]] = game['stats']
        return sum(s.get('finals', 0) for s in stats.values())

    @property
    async def beds(self) -> int | None:
        """
        Get the total beds broken across all games.

        Returns:
            int | None: Sum of beds broken, or None if unavailable.
        """
        game = await self.fetch_game_stats()
        if not game or 'stats' not in game:
            return None

        stats: dict[str, dict[str, Any]] = game['stats']
        return sum(s.get('beds', 0) for s in stats.values())

    @property
    async def guild_role(self) -> str | None:
        """
        Get the player's guild role.

        Returns:
            str | None: Guild role (OWNER, ADMIN, MODERATOR, or MEMBER),
            or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get('guildRole') if guild else None

    @property
    async def guild_join_time(self) -> int | None:
        """
        Get the time the player joined their guild.

        Returns:
            int | None: UNIX timestamp in seconds, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get('joinTime') if guild else None

    @property
    async def guild_id(self) -> str | None:
        """
        Get the player's guild ID.

        Returns:
            str | None: Guild ID, or None if unavailable.
        """
        guild = await self.fetch_guild_info()
        return guild.get('guildId') if guild else None