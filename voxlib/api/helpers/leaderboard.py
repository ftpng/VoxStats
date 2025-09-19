from typing import Any

from voxlib.api import API, VoxylApiEndpoint


class LeaderboardInfo:
    """
    Helper class for fetching leaderboard data from the Voxyl Network API.
    """

    @staticmethod
    async def fetch_leaderboard(
        type_: str, num: int = 100
    ) -> dict[str, Any] | None:
        """
        Fetch the normal leaderboard.

        Args:
            type_ (str): "weightedwins" or "level".
            num (int, optional): Number of rows to retrieve (max 100).
                Defaults to 100.

        Returns:
            dict | None: Full JSON response from the API,
            or None if unavailable.
        """
        return await API.make_request(
            VoxylApiEndpoint.LEADERBOARD_NORMAL,
            type=type_,
            num=num
        )

    @staticmethod
    async def fetch_game_leaderboard(
        ref: str, period: str = "weekly", type_: str = "wins"
    ) -> dict[str, Any] | None:
        """
        Fetch the game leaderboard for a specific game reference.

        Args:
            ref (str): The game reference (use `/join list` in-game to view all).
            period (str, optional): "weekly" or "daily". Defaults to "weekly".
            type_ (str, optional): "wins" or "winstreaks". Defaults to "wins".

        Returns:
            dict | None: Full JSON response from the API,
            or None if unavailable.
        """
        return await API.make_request(
            VoxylApiEndpoint.LEADERBOARD_GAME,
            ref=ref,
            period=period,
            type=type_
        )