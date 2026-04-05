# ─────────────────────────────────────────────
#  save_load.py  —  збереження / завантаження
# ─────────────────────────────────────────────
import json
import os
from settings_mobile import SAVE_FILE


def save(game_state) -> bool:
    """
    Зберігає поточний стан гри у JSON-файл.
    Повертає True при успіху, False при помилці.
    """
    try:
        data = game_state.to_dict()
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[save_load] Помилка збереження: {e}")
        return False


def load(game_state) -> float:
    """
    Завантажує стан із JSON-файлу в переданий об'єкт GameState.
    Повертає кількість монет офлайн-прогресу (0.0 якщо збереження немає).
    """
    if not os.path.exists(SAVE_FILE):
        return 0.0

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        offline_earned = game_state.from_dict(data)
        return offline_earned or 0.0
    except Exception as e:
        print(f"[save_load] Помилка завантаження: {e}")
        return 0.0


def delete_save() -> bool:
    """Видаляє файл збереження (корисно для кнопки 'Новa гра')."""
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        return True
    except Exception as e:
        print(f"[save_load] Помилка видалення: {e}")
        return False