def get_xp_for_level(level: int) -> int:
    """
    Calculate the XP required to reach a given level.

    Args:
        level (int): The players level.

    Returns:
        int: The amount of XP required to progress from this level
             to the next.
    """
    cycle = {
        0: 1000,
        1: 2000,
        2: 3000,
        3: 4000,
        4: 5000
    }

    block = level // 100

    if level % 100 in cycle:
        return cycle[level % 100]

    if block == 0:
        return 5000
    elif block == 1:
        return 5500
    elif block == 2:
        return 6000
    elif block == 3:
        return 6500
    elif block == 4:
        return 7000
    elif block == 5:
        return 7500
    elif block == 6:
        return 8000
    elif block == 7:
        return 8500
    elif block == 8:
        return 9000
    elif block == 9:
        return 9500
    else:
        return 10000
