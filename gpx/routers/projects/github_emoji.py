import httpx
import re
import asyncio
from typing import Dict

GITHUB_EMOJI_API_URL = "https://api.github.com/emojis"


async def fetch_github_emojis() -> Dict[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(GITHUB_EMOJI_API_URL)
        response.raise_for_status()
        return response.json()


def extract_emoji_code(url: str) -> str:
    return url.split("/")[-1].split(".")[0]


async def generate_github_emoji_map() -> Dict[str, str]:
    emoji_data = await fetch_github_emojis()
    return {f":{key}:": extract_emoji_code(value) for key, value in emoji_data.items()}

try:
    GITHUB_EMOJI_MAP = asyncio.run(generate_github_emoji_map())
except:
    GITHUB_EMOJI_MAP = {}


def get_github_emoji_map() -> Dict[str, str]:
    return GITHUB_EMOJI_MAP


GITHUB_EMOJI_MAP = get_github_emoji_map()


def replace_github_emojis(text):
    def replace_emoji(match):
        emoji_code = GITHUB_EMOJI_MAP.get(match.group(0), match.group(0))
        return (
            chr(int(emoji_code, 16)) if emoji_code.startswith("1f") else match.group(0)
        )

    pattern = re.compile("|".join(map(re.escape, GITHUB_EMOJI_MAP.keys())))
    return pattern.sub(replace_emoji, text)


if __name__ == "__main__":
    emoji_map = get_github_emoji_map()
    print(f"Total emojis: {len(emoji_map)}")
    print("Sample entries:")
    for key, value in list(emoji_map.items())[:5]:
        print(f"{key}: {value}")
