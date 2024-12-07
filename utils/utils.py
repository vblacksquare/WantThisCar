
from datetime import datetime, timezone


def group_by(target, k=5) -> list:
    return [target[i:i+k] for i in range(0, len(target), k)]


def now() -> int:
    return round(datetime.now(timezone.utc).timestamp())


def beautify_num(num: int, splitter: str = "'") -> str:
    string = str(num)
    groups = group_by(string[::-1], k=3)

    return splitter.join((
        part[::-1]
        for part in groups[::-1]
    ))


async def create_join_link(bot, is_group=False, is_channel=False):
    if is_group:
        dest = "group"

    elif is_channel:
        dest = "channel"

    else:
        raise ValueError("Chat type is not specifed should be is_group=True or is_channel=True")

    return f"https://t.me/{(await bot.get_me()).username}?start{dest}=&admin=pin_messages+post_messages+edit_messages+delete_messages+manage_chat+invite_users"
