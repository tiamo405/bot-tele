import os
from typing import Dict, List

import config
from utils.json_storage import JSONStorage


NOTIFICATION_FILE = os.path.join(config.DATA_DIR, "notification_channels.json")

DEFAULT_CHANNELS: Dict[str, Dict[str, str]] = {
    "reminder_lunch": {"title": "Nhắc ăn trưa"},
    "reminder_badminton": {"title": "Nhắc cầu lông"},
    "reminder_tet": {"title": "Nhắc lễ / Tết"},
    "schedule_aug": {"title": "Giá vàng"},
    "schedule_silver": {"title": "Giá bạc"},
}

_storage = JSONStorage(NOTIFICATION_FILE, default_data={"channels": {}})


def _load_data() -> Dict:
    data = _storage.load()
    if not isinstance(data, dict):
        data = {}

    channels = data.get("channels")
    if not isinstance(channels, dict):
        channels = {}

    data["channels"] = channels
    return data


def _save_data(data: Dict) -> bool:
    return _storage.save(data)


def list_channels() -> List[str]:
    data = _load_data()
    channel_ids = set(DEFAULT_CHANNELS.keys()) | set(data.get("channels", {}).keys())
    return sorted(channel_ids)


def get_channel_info(channel_key: str) -> Dict[str, object]:
    data = _load_data()
    channel_data = data.get("channels", {}).get(channel_key, {})
    defaults = DEFAULT_CHANNELS.get(channel_key, {})

    chat_ids = channel_data.get("chat_ids", [])
    if not isinstance(chat_ids, list):
        chat_ids = []

    return {
        "key": channel_key,
        "title": channel_data.get("title") or defaults.get("title") or channel_key,
        "enabled": bool(channel_data.get("enabled", True)),
        "chat_ids": chat_ids,
    }


def list_all_channels() -> List[Dict[str, object]]:
    return [get_channel_info(channel_key) for channel_key in list_channels()]


def get_chat_ids(channel_key: str) -> List[int]:
    info = get_channel_info(channel_key)
    if not info["enabled"]:
        return []

    return [int(chat_id) for chat_id in info["chat_ids"]]


def set_channel_enabled(channel_key: str, enabled: bool) -> None:
    data = _load_data()
    channels = data.setdefault("channels", {})
    channel = channels.get(channel_key, {})

    if not isinstance(channel, dict):
        channel = {}

    channel.setdefault("chat_ids", [])
    if channel_key in DEFAULT_CHANNELS and not channel.get("title"):
        channel["title"] = DEFAULT_CHANNELS[channel_key]["title"]

    channel["enabled"] = bool(enabled)
    channels[channel_key] = channel
    _save_data(data)


def add_chat_id(channel_key: str, chat_id: int) -> bool:
    data = _load_data()
    channels = data.setdefault("channels", {})
    channel = channels.get(channel_key, {})

    if not isinstance(channel, dict):
        channel = {}

    chat_ids = channel.get("chat_ids", [])
    if not isinstance(chat_ids, list):
        chat_ids = []

    chat_id = int(chat_id)
    if chat_id in chat_ids:
        return False

    chat_ids.append(chat_id)
    channel["chat_ids"] = chat_ids
    channel.setdefault("enabled", True)
    if channel_key in DEFAULT_CHANNELS and not channel.get("title"):
        channel["title"] = DEFAULT_CHANNELS[channel_key]["title"]

    channels[channel_key] = channel
    _save_data(data)

    return True


def remove_chat_id(channel_key: str, chat_id: int) -> bool:
    data = _load_data()
    channels = data.get("channels", {})
    channel = channels.get(channel_key)

    if not isinstance(channel, dict):
        return False

    chat_ids = channel.get("chat_ids", [])
    if not isinstance(chat_ids, list):
        return False

    chat_id = int(chat_id)
    if chat_id not in chat_ids:
        return False

    chat_ids.remove(chat_id)
    channel["chat_ids"] = chat_ids
    channels[channel_key] = channel
    _save_data(data)

    return True


def find_chat_assignments(chat_id: int) -> List[Dict[str, object]]:
    data = _load_data()
    assignments = []

    for channel_key in list_channels():
        channel = data.get("channels", {}).get(channel_key, {})
        chat_ids = channel.get("chat_ids", []) if isinstance(channel, dict) else []
        if not isinstance(chat_ids, list):
            continue

        if int(chat_id) in [int(item) for item in chat_ids]:
            defaults = DEFAULT_CHANNELS.get(channel_key, {})
            assignments.append({
                "key": channel_key,
                "title": channel.get("title") or defaults.get("title") or channel_key,
                "enabled": bool(channel.get("enabled", True)) if isinstance(channel, dict) else True,
            })

    return assignments


def get_channel_members(channel_key: str) -> List[int]:
    info = get_channel_info(channel_key)
    return [int(chat_id) for chat_id in info["chat_ids"]]
