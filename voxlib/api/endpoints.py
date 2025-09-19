from enum import Enum


class VoxylApiEndpoint(Enum):
    """
    Enumeration of all available Voxyl Network API endpoints.

    Each member corresponds to a specific REST API path, with placeholders
    for required parameters such as `{uuid}`, `{discord_id}`, `{tag}`, `{id}`, etc.

    This enum only provides endpoint definitions and does not execute requests.
    """

    PLAYER_INFO = "player/info/{uuid}"
    PLAYER_OVERALL = "player/stats/overall/{uuid}"
    PLAYER_STATS = "player/stats/game/{uuid}"
    PLAYER_GUILD = "player/guild/{uuid}"
    PLAYER_RANKING = "player/ranking/{uuid}"

    GUILD_INFO = "guild/info/{tag_or_id}"
    GUILD_MEMBERS = "guild/members/{tag_or_id}"
    GUILD_TOP = "guild/top"

    LEADERBOARD_NORMAL = "leaderboard/normal"
    LEADERBOARD_GAME = "leaderboard/game/{ref}"

    DISCORD_FROM_PLAYER = "integration/discord_from_player/{uuid}"
    PLAYER_FROM_DISCORD = "integration/player_from_discord/{discord_id}"