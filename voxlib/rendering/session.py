from mctextrender import BackgroundImageLoader, ImageRender

from voxlib.api.utils import PlayerInfo
from voxlib.database.utils import Sessions
from voxlib import DIR, get_xp_and_stars, started_on

from .utils import get_displayname, get_progress_bar, render_skin


async def render_session(uuid: str, session: int) -> None:
    path = f"{DIR}assets/bg/sessions/base.png"
    bg = BackgroundImageLoader(path)
    base_img = bg.load_image(path).convert("RGBA")
    im = ImageRender(base_img)

    player = PlayerInfo(uuid)

    session_data = Sessions(uuid, session).get_session()
    if not session_data:
        return None

    im.text.draw_many([
        (f'&fWins', {'position': (404, 185), "align": "center", "font_size": 16}),
        (f'&fWeighted Wins', {'position': (649, 185), "align": "center", "font_size": 16}),

        (f'&fFinal Kills', {'position': (363, 265), "align": "center", "font_size": 16}),
        (f'&fKills', {'position': (526, 265), "align": "center", "font_size": 16}),
        (f'&fBeds Broken', {'position': (690, 265), "align": "center", "font_size": 16}),

        (f'&fLevels Gained', {'position': (404, 340), "align": "center", "font_size": 16}),
        (f'&fEXP Gained', {'position': (649, 340), "align": "center", "font_size": 16}),
        
        (f'&fBWP Stats (Overall)', {'position': (631, 138), "align": "center", "font_size": 14}),
        (f'&fSession &8(&7#{session}&8)', {'position': (386, 138), "align": "center", "font_size": 14}),
    ],
        {"shadow_offset": (2, 2)} 
    )

    wins = int(await player.wins - session_data[2])
    weighted = int(await player.weightedwins - session_data[3]) 
    kills = int(await player.kills - session_data[4]) 
    finals = int(await player.finals - session_data[5])
    beds = int(await player.beds - session_data[6])

    exp_gained, stars_gained = await get_xp_and_stars(
        old_level = session_data[7],
        old_xp = session_data[8],
        new_level = await player.level,
        new_xp = await player.exp
    )

    display_name = await get_displayname(uuid)
    parts = await get_progress_bar(uuid)

    started = started_on(session_data[9])


    im.text.draw_many([
        (f'&a{wins:,}', {'position': (404, 207), "align": "center", "font_size": 20}),
        (f'&9{weighted:,}', {'position': (649, 207), "align": "center", "font_size": 20}),

        (f'&d{finals:,}', {'position': (363, 287), "align": "center", "font_size": 20}),
        (f'&c{kills:,}', {'position': (526, 287), "align": "center", "font_size": 20}),
        (f'&e{beds:,}', {'position': (690, 287), "align": "center", "font_size": 20}),

        (f'&b{stars_gained}', {'position': (404, 362), "align": "center", "font_size": 18}),
        (f'&b{exp_gained:,}', {'position': (649, 362), "align": "center", "font_size": 18}),

        (f'{display_name}', {'position': (526, 50), "align": "center", "font_size": 20}),

        (f'{parts[0]}',   {'position': (446, 413), 'align': 'right',   'font_size': 16}),
        (f'{parts[1]}', {'position': (526, 411), 'align': 'center', 'font_size': 16}),
        (f'{parts[2]}',  {'position': (609, 413), 'align': 'left',  'font_size': 16}),

        (f'Started {started}',  {'position': (526, 98), 'align': 'center',  'font_size': 14}),
    ],
        {"shadow_offset": (2, 2)} 
    )

    await render_skin(
        image=im._image, 
        uuid=uuid, 
        position=(55, 95),
        size=(204, 374),
        style='full'
    )
    im.save(f"{DIR}assets/stats/session.png")