from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .xp_map import get_xp_for_level


async def get_total_xp(level: int, partial_xp: int = 0) -> int:
    """
    Calculate the total XP a player has accumulated up to a given level.

    Args:
        level (int): The players current level.
        partial_xp (int, optional): XP progress within the current level.
            Defaults to 0.

    Returns:
        int: The total accumulated XP.
    """
    total_xp = 0
    for lvl in range(1, level):
        total_xp += get_xp_for_level(lvl)

    total_xp += partial_xp
    return total_xp


async def get_xp_and_stars(
    old_level: int,
    old_xp: int,
    new_level: int,
    new_xp: int
) -> tuple[int, float]:
    """
    Calculate how much XP and how many stars a player gained
    between two points in time.

    Stars are awarded at a fixed rate of 5000 XP per star.

    Args:
        old_level (int): The players previous level.
        old_xp (int): The partial XP progress within the previous level.
        new_level (int): The players current level.
        new_xp (int): The partial XP progress within the current level.

    Returns:
        tuple[int, float]: A tuple containing:
            - Total XP gained (int)
            - Stars gained (float, rounded to 2 decimals)
    """
    old = await get_total_xp(old_level, old_xp)
    new = await get_total_xp(new_level, new_xp)

    xp_gained = new - old
    stars_gained = round(xp_gained / 5000, 2)

    return xp_gained, stars_gained


def started_on(date_input) -> str:
    """
    Convert a given datetime or string into a formatted start date with a relative time description.

    The function takes a datetime object or a string representing a datetime in the format 
    ``"%Y-%m-%d %H:%M:%S"``. It calculates how long ago that date was relative to the current time, 
    and returns a string with the formatted date and a human-readable "time ago" expression.

    Args:
        date_input (datetime | str): A datetime object or a string in the format 
            ``"%Y-%m-%d %H:%M:%S"`` representing the start date.

    Returns:
        str: A string containing the formatted date in ``"DD/MM/YYYY"`` format, followed by 
        the relative time ago (e.g., ``"15/03/2022 (2 years ago)"``).
    """
    if isinstance(date_input, datetime):
        past = date_input
    else:
        past = datetime.strptime(str(date_input), "%Y-%m-%d %H:%M:%S")

    now = datetime.now()
    delta = relativedelta(now, past)

    if delta.years:
        ago = f"{delta.years} year{'s' if delta.years > 1 else ''} ago"
    elif delta.months:
        ago = f"{delta.months} month{'s' if delta.months > 1 else ''} ago"
    elif delta.days >= 7:
        weeks = delta.days // 7
        ago = f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif delta.days:
        ago = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.hours:
        ago = f"{delta.hours} hr{'s' if delta.hours > 1 else ''} ago"
    elif delta.minutes:
        ago = f"{delta.minutes} min{'s' if delta.minutes > 1 else ''} ago"
    else:
        ago = f"{delta.seconds} sec{'s' if delta.seconds > 1 else ''} ago"

    date_formatted = past.strftime("%d/%m/%Y")
    return f"{date_formatted} ({ago})"