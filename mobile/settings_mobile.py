# ─────────────────────────────────────────────
#  settings_mobile.py
#  Константи компонування для мобільної версії.
#  Кольори, апгрейди, досягнення тощо беруться
#  з settings.py (спільний файл).
# ─────────────────────────────────────────────
import pygame

# ── Вікно ─────────────────────────────────────
# На реальному пристрої: pygame.display.set_mode((0,0))
# повертає повний розмір екрану.
# Для тестування на ПК — фіксований розмір.
MOBILE_DEFAULT_W = 480
MOBILE_DEFAULT_H = 854
FPS              = 60
WINDOW_TITLE     = "Clicker Game"

# ── Розміри зон ───────────────────────────────
# Верхній бар ресурсів (монети / сек / за клік) — незмінний
RES_BAR_H   = 80

# Нижній бар вкладок
TAB_BAR_H   = 72

# Ширина однієї кнопки вкладки (щоб усі 7 не тіснились)
TAB_BTN_W   = 90

# Назви вкладок — порядок відображення знизу
TAB_HOME         = "home"
TAB_CLICK        = "click"
TAB_WORKERS      = "workers"
TAB_REBIRTH      = "rebirth"
TAB_ACHIEVEMENTS = "achievements"
TAB_STATS        = "stats"
TAB_SETTINGS     = "settings"

TABS_MOBILE = [
    TAB_HOME,
    TAB_CLICK,
    TAB_WORKERS,
    TAB_REBIRTH,
    TAB_ACHIEVEMENTS,
    TAB_STATS,
    TAB_SETTINGS,
]

# Підписи вкладок (без емодзі)
TAB_LABELS = {
    TAB_HOME:         "Головна",
    TAB_CLICK:        "Клік",
    TAB_WORKERS:      "Наймання",
    TAB_REBIRTH:      "Перерод.",
    TAB_ACHIEVEMENTS: "Досягн.",
    TAB_STATS:        "Стат.",
    TAB_SETTINGS:     "Налашт.",
}

# Іконки вкладок (файли; якщо нема — малюємо текст)
TAB_ICONS = {
    TAB_HOME:         "assets/images/icons/tab_home.png",
    TAB_CLICK:        "assets/images/icons/tab_click.png",
    TAB_WORKERS:      "assets/images/icons/tab_workers.png",
    TAB_REBIRTH:      "assets/images/icons/tab_rebirth.png",
    TAB_ACHIEVEMENTS: "assets/images/icons/tab_ach.png",
    TAB_STATS:        "assets/images/icons/tab_stats.png",
    TAB_SETTINGS:     "assets/images/icons/tab_settings.png",
}

# ── Монета ────────────────────────────────────
# Радіус підбирається динамічно в ui_mobile.py
# залежно від реального розміру екрану.
# Тут — базові коефіцієнти від ширини екрану.
COIN_RADIUS_RATIO = 0.28   # радіус = W * 0.28
COIN_GLOW_RATIO   = 0.36   # ореол  = W * 0.36

# ── Картки апгрейдів ──────────────────────────
CARD_H    = 82    # висота картки (px)
CARD_MRG  = 8     # відступ між картками
CARD_PAD  = 12    # внутрішній відступ картки
ICON_SIZE = 54    # розмір іконки в картці

# ── Досягнення — сітка ────────────────────────
ACH_COLS  = 4     # стовпців у сітці (менше, ніж Desktop)
ACH_ICON  = 68    # розмір іконки досягнення
ACH_PAD   = 10    # відступ між іконками

# ── Слайдер гучності ──────────────────────────
SLIDER_H  = 20    # висота треку слайдера

# ── Кнопки (загальні) ─────────────────────────
BTN_H     = 54    # висота типової кнопки
BTN_R     = 10    # радіус заокруглення

# ── Спливаючі числа ───────────────────────────
# (швидкість і тривалість успадковуються з settings.py)

# ── Кольори (мобільна тема — та ж, що Desktop) ─
# Імпортуємо з settings.py щоб не дублювати
from settings import (
    COLOR_BG, COLOR_TOP_BAR, COLOR_TOP_BAR_BORDER,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_TAB_ACTIVE, COLOR_TAB_INACTIVE, COLOR_TAB_HOVER, COLOR_TAB_BORDER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_LOCKED,
    COLOR_COIN_VAL, COLOR_PASSIVE, COLOR_CPC,
    COLOR_BTN_NORMAL, COLOR_BTN_HOVER, COLOR_BTN_LOCKED,
    COLOR_BTN_BORDER, COLOR_BTN_BORDER_HOV,
    COLOR_POPUP,
    COLOR_TOGGLE_ON, COLOR_TOGGLE_OFF, COLOR_TOGGLE_KNOB,
    COLOR_DELETE_BTN, COLOR_DELETE_CONFIRM, COLOR_DELETE_TEXT,
    COLOR_REBIRTH_BTN, COLOR_REBIRTH_HOVER, COLOR_REBIRTH_LOCKED,
    COLOR_REBIRTH_TEXT, COLOR_REBIRTH_GLOW,
    COLOR_ACH_UNLOCKED, COLOR_ACH_LOCKED,
    COLOR_ACH_BORDER_ON, COLOR_ACH_BORDER_OFF,
    COIN_IMAGE_TEMPLATE, COIN_CLICK_SCALE,
    MUSIC_FILE, UPGRADES, ACHIEVEMENTS, OFFLINE_INCOME_CAP, POPUP_LIFETIME, POPUP_SPEED, MAX_CLICKS_PER_SEC, REBIRTH_BASE_COST, COIN_ANIM_SPEED, SAVE_FILE, COIN_BASE_RADIUS, COIN_GLOW_RADIUS,
)