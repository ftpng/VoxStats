from PIL import Image, UnidentifiedImageError
from mctextrender import ImageRender
from typing import List
from mcfetch import Player
from io import BytesIO

from voxlib import mojang_session, get_xp_for_level
from voxlib.api.utils import PlayerInfo
from voxlib.api import fetch_skin_model


def get_role_prefix(role: str) -> str:
    """
    Return the formatted chat prefix for a given role.

    Args:
        role (str): The player's role name (e.g., "Owner", "Admin", "Legend").

    Returns:
        str: The color-coded role prefix, or a default gray code if the role is unknown.
    """
    role_prefixes = {
        "Owner": "&c[Owner] ",
        "Admin": "&c[Admin] ",
        "Manager": "&4[Manager] ",
        "Dev": "&a[Dev] ",
        "HeadBuilder": "&5[HeadBuilder] ",
        "Builder": "&d[Builder] ",
        "SrMod": "&e[SrMod] ",
        "Mod": "&e[Mod] ",
        "Trainee": "&a[Trainee] ",
        "Youtube": "&c[&fYoutube&c] ",
        "Master": "&6[Master] ",
        "Expert": "&9[Expert] ",
        "Adept": "&2[Adept] ",
        "Legend": "&6[Leg&een&fd&6] ",
    }
    return role_prefixes.get(role, "&7")


async def get_displayname(uuid: str) -> str:
    """
    Build a player's display name including role prefix and special Legend styling.

    Args:
        uuid (str): The player's UUID.

    Returns:
        str: The formatted display name with role prefix and color codes.
    """
    player = PlayerInfo(uuid)

    role = await player.role
    name = Player(player=uuid, requests_obj=mojang_session).name

    if role == "Legend":
        if len(name) >= 3:
            name = '&6' + name[:-3] + '&e' + name[-3:-1] + '&f' + name[-1]
        elif len(name) == 2:
            name = '&6' + name[0] + '&6' + name[1]
        elif len(name) == 1:
            name = '&6' + name

    rank = get_role_prefix(role)

    return f"{rank}{name}"


class PrestigeColorMaps:
    """
    Containers for prestige color mappings and 1000+ level color cycle.
    """
    prestige_map = {
        900: '&5',
        800: '&9',
        700: '&d',
        600: '&4',
        500: '&3',
        400: '&2',
        300: '&b',
        200: '&6',
        100: '&f',
        0: '&7',
    }

    prestige_1000_colors = (
        '&c',
        '&6',
        '&e',
        '&a',
        '&b',
        '&d',
        '&5',
    )


bedwars_star_symbol_map = {
    3100: '✥',
    2100: '⚝',
    1100: '✪',
    0: '✫'
}


def get_star_symbol(level: int) -> str:
    """
    Return the star symbol used when rendering a level badge.

    Args:
        level (int): The player's level.

    Returns:
        str: The star symbol character.
    """
    return '✫'


def get_prestige_color(level: int) -> str:
    """
    Render a level badge with prestige-based color codes.

    Args:
        level (int): The player's level. If a dict is provided, the 'level' key is used.

    Raises:
        TypeError: If level is not an int or a dict containing an int under 'level'.

    Returns:
        str: The color-coded level string, e.g., "&6[123✫]".
    """
    if isinstance(level, dict):
        level = level.get('level', 0)

    if not isinstance(level, int):
        raise TypeError(
            f"Expected an integer for level, but got {type(level)}")

    c = PrestigeColorMaps
    level_str = f"[{level}{get_star_symbol(level)}]"

    if level < 1000:
        for threshold in sorted(c.prestige_map.keys(), reverse=True):
            if level >= threshold:
                color = c.prestige_map[threshold]
                return ''.join([f"{color}{char}" for char in level_str])

    color = c.prestige_1000_colors
    return ''.join([f"{color[i % len(color)]}{char}" for i, char in enumerate(level_str)])


def get_prestige_color_level(level: int) -> str:
    """
    Convenience wrapper to return the prestige-colored level badge.

    Args:
        level (int): The player's level.

    Returns:
        str: The color-coded level string.
    """
    return get_prestige_color(level)


async def get_progress_bar(uuid: str) -> List[str]:
    """
    Build a progress bar line showing current level, XP progress, and next level.

    Args:
        uuid (str): The player's UUID.

    Returns:
        List[str]: A three-part list containing the left badge, the bar, and the right badge.
    """
    progress_symbol = "⏹"
    progress_bar_max = 10

    player = PlayerInfo(uuid)

    level = await player.level
    xp = await player.exp

    xp_needed = get_xp_for_level(level)

    if xp is None or xp <= 0 or xp_needed is None:
        xp_needed = 5000
        bar = f"&7{progress_symbol * progress_bar_max}"
    else:
        ratio = xp / xp_needed
        colored_chars = max(1, int(progress_bar_max * ratio))
        colored_chars = min(colored_chars, progress_bar_max)
        gray_chars = progress_bar_max - colored_chars

        colored_progress = f"&b{progress_symbol * colored_chars}"
        gray_progress = f"&7{progress_symbol * gray_chars}"

        bar = colored_progress + gray_progress

    new_level = int(level + 1)

    cur_level = get_prestige_color_level(level)
    next_level = get_prestige_color_level(new_level)

    return [
        f"{cur_level} &8[",
        f"{bar}",
        f"&8] {next_level}"
    ]


async def render_skin(
    image: Image.Image,
    uuid: str,
    position: tuple[int, int],
    size: tuple[int, int],
    style: str = 'full'
) -> None:
    """
    Paste a player's skin onto the provided Pillow image.

    Args:
        image (Image.Image): The Pillow image to paste onto (must be the same one wrapped by ImageRender).
        uuid (str): The player's UUID.
        position (tuple[int, int]): (x, y) coordinates for placing the skin.
        size (tuple[int, int]): (width, height) of the resized skin.
        style (str): Skin style ("full", etc.).
    """
    try:
        skin_data = await fetch_skin_model(uuid, style)
        skin_model = BytesIO(skin_data)
        skin = Image.open(skin_model).convert("RGBA").resize(size)

        image.paste(skin, position, mask=skin.split()[3])
    except (UnidentifiedImageError, Exception) as error:
        print("render_skin error:", error)
