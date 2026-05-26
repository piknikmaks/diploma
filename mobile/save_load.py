# ─────────────────────────────────────────────
#  save_load.py  —  збереження / завантаження
# ─────────────────────────────────────────────
import json
import os

IS_ANDROID = (
    "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_BOOTLOGO" in os.environ
    or "ANDROID_PRIVATE" in os.environ
)

_save_file = None


def get_save_path() -> str:
    """Шлях до save.json. На Android — приватна папка застосунку."""
    if IS_ANDROID:
        base = (
            os.environ.get("ANDROID_PRIVATE")
            or os.environ.get("ANDROID_APP_PATH")
            or os.path.expanduser("~")
        )
        save_dir = os.path.join(base, "saves")
    else:
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "MyClickerGame")

    try:
        os.makedirs(save_dir, exist_ok=True)
    except OSError as e:
        print(f"[save_load] mkdir failed: {e}")
        save_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(save_dir, "save.json")


def _save_file_path() -> str:
    global _save_file
    if _save_file is None:
        _save_file = get_save_path()
    return _save_file


def save(game_state) -> bool:
    try:
        path = _save_file_path()
        data = game_state.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[save_load] save error: {e}")
        return False


def load(game_state) -> float:
    path = _save_file_path()
    if not os.path.exists(path):
        return 0.0

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            return 0.0
        data = json.loads(raw)
        offline_earned = game_state.from_dict(data)
        return offline_earned or 0.0
    except Exception as e:
        print(f"[save_load] load error: {e}")
        return 0.0


def delete_save() -> bool:
    try:
        path = _save_file_path()
        if os.path.exists(path):
            os.remove(path)
        return True
    except Exception as e:
        print(f"[save_load] delete error: {e}")
        return False
