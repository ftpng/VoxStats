from typing import Optional
from voxlib.database import ensure_cursor, Cursor


class Linking:
    """
    Manages linking between a Discord user ID and a player UUID in the database.
    """

    def __init__(self, discord_id: int) -> None:
        """
        Initialize a Linking instance for a specific Discord user.

        Args:
            discord_id (int): The unique ID of the Discord user.
        """
        self._discord_id = discord_id

    @ensure_cursor
    def get_linked_player(self, *, cursor: Cursor = None) -> Optional[dict]:
        """
        Retrieve the player UUID linked to this Discord user, if any.

        Args:
            cursor (Cursor, optional): Database cursor. If not provided,
                a new connection and cursor are created automatically.

        Returns:
            Optional[dict]: A dictionary representing the linked record
            (containing Discord ID and player UUID), or None if no link exists.
        """
        cursor.execute(
            "SELECT * FROM linked WHERE discord_id = %s", (self._discord_id,)
        )
        linked_data = cursor.fetchone()

        if linked_data:
            return linked_data
        return None

    @ensure_cursor
    def link_player(self, uuid: str, *, cursor: Cursor = None) -> None:
        """
        Link a Discord user to a player UUID.  
        If the Discord user is already linked, the UUID is updated.

        Args:
            uuid (str): The player UUID to link with the Discord user.
            cursor (Cursor, optional): Database cursor. If not provided,
                a new connection and cursor are created automatically.
        """
        cursor.execute(
            "SELECT * FROM linked WHERE discord_id=%s", (self._discord_id,)
        )
        linked_data = cursor.fetchone()

        if not linked_data:
            cursor.execute(
                "INSERT INTO linked (discord_id, uuid) VALUES (%s, %s)",
                (self._discord_id, uuid),
            )
        else:
            cursor.execute(
                "UPDATE linked SET uuid=%s WHERE discord_id=%s",
                (uuid, self._discord_id),
            )

    @ensure_cursor
    def unlink_player(self, *, cursor: Cursor = None) -> None:
        """
        Remove the link between this Discord user and any player UUID.

        Args:
            cursor (Cursor, optional): Database cursor. If not provided,
                a new connection and cursor are created automatically.
        """
        cursor.execute(
            "DELETE FROM linked WHERE discord_id=%s", (self._discord_id,)
        )
