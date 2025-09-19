from os import getenv
from typing import Text

from dotenv import load_dotenv; load_dotenv()
from requests_cache import CachedSession


TOKEN: Text = getenv('TOKEN')
VERSION: str = "2.0.0"

COLOR_GREEN: int = 0x32BA7C
COLOR_RED: int = 0xF15249
COLOR_YELLOW: int = 0xF8C049
COLOR_BLUE: int = 0x5555FF

mojang_session = CachedSession(
    cache_name="voxlib/.cache/mojang_cache", 
    expire_after=60
)