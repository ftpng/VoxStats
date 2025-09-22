from typing import Optional, Tuple

from voxlib.database import ensure_cursor, async_ensure_cursor, Cursor
from voxlib.api.utils import PlayerInfo


class Sessions:
    """
    Represents a player's game session on the Voxyl network.
    """

    def __init__(self, uuid: str, session_id: int = None) -> None:
        """
        Initialize a session instance.

        Args:
            uuid (str): The unique identifier (UUID) of the player.
            session_id (int, optional): The session identifier. Defaults to None.
        """
        self._uuid = uuid
        self._session_id = session_id

    @ensure_cursor
    def get_session(self, *, cursor: Cursor = None) -> Optional[Tuple]:
        """
        Retrieve a session record for the player.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.

        Returns:
            Optional[Tuple]: A tuple containing session data if found, otherwise None.
        """
        cursor.execute(
            "SELECT * FROM sessions WHERE uuid=%s AND session_id=%s",
            (self._uuid, self._session_id)
        )
        result = cursor.fetchone()
        return result if result else None

    @async_ensure_cursor
    async def create_session(self, *, cursor: Cursor = None) -> None:
        """
        Create a new session record for the player in the database.

        Player statistics are fetched from the Voxyl API and stored with
        the current timestamp as the session start time.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.
        """
        player = PlayerInfo(self._uuid)
        cursor.execute(
            """
            INSERT INTO sessions (
                uuid, wins, weighted, kills, finals, beds, star, xp, start_date, session_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
            """, (
                self._uuid,
                await player.wins,
                await player.weightedwins,
                await player.kills,
                await player.finals,
                await player.beds,
                await player.level,
                await player.exp,
                self._session_id,
            )
        )

    @async_ensure_cursor
    async def reset_session(self, *, cursor: Cursor = None) -> None:
        """
        Reset (update) an existing session with the player's latest statistics.

        The session start time is also updated to the current timestamp.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.
        """
        player = PlayerInfo(self._uuid)
        cursor.execute(
            """
            UPDATE sessions
            SET wins=%s, weighted=%s, kills=%s, finals=%s, beds=%s, star=%s, xp=%s, start_date=NOW()
            WHERE uuid=%s AND session_id=%s
            """, (
                await player.wins,
                await player.weightedwins,
                await player.kills,
                await player.finals,
                await player.beds,
                await player.level,
                await player.exp,
                self._uuid,
                self._session_id,
            )
        )

    @ensure_cursor
    def end_session(self, *, cursor: Cursor = None) -> None:
        """
        Delete a session record from the database.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.
        """
        cursor.execute(
            "DELETE FROM sessions WHERE uuid=%s AND session_id=%s",
            (self._uuid, self._session_id)
        )

    @ensure_cursor
    def get_active_sessions(self, *, cursor: Cursor = None) -> Optional[Tuple]:
        """
        Fetch all active session IDs for the player.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.

        Returns:
            Optional[Tuple]: A tuple of session IDs if found, otherwise None.
        """
        cursor.execute(
            "SELECT session_id FROM sessions WHERE uuid=%s",
            (self._uuid,)
        )
        result = cursor.fetchall()
        return result if result else None

    @ensure_cursor
    def get_start_date(self, *, cursor: Cursor = None) -> Optional[str]:
        """
        Get the start date of a specific session.

        Args:
            cursor (Cursor, optional): Active database cursor. Defaults to None.

        Returns:
            Optional[str]: The session start timestamp as a string if found, otherwise None.
        """
        cursor.execute(
            "SELECT start_date FROM sessions WHERE uuid=%s AND session_id=%s",
            (self._uuid, self._session_id)
        )
        result = cursor.fetchone()
        return result[0] if result else None
