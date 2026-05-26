# ─────────────────────────────────────────────
#  settings_mobile.py
#  Константи компонування для мобільної версії.
# ─────────────────────────────────────────────

# Еталонний макет (усі розміри нижче — для цього роздільення)
DESIGN_W = 480
DESIGN_H = 854

MOBILE_DEFAULT_W = DESIGN_W
MOBILE_DEFAULT_H = DESIGN_H
FPS              = 60
WINDOW_TITLE     = "Clicker Game"

# Масштаб відносно еталону (оновлюється apply_layout)
SCALE = 1.0

# ── Розміри зон (масштабуються через apply_layout) ──
RES_BAR_H   = 80
TAB_BAR_H   = 72
TAB_BTN_W   = 90

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

TAB_LABELS = {
    TAB_HOME:         "Головна",
    TAB_CLICK:        "Клік",
    TAB_WORKERS:      "Наймання",
    TAB_REBIRTH:      "Перерод.",
    TAB_ACHIEVEMENTS: "Досягн.",
    TAB_STATS:        "Стат.",
    TAB_SETTINGS:     "Налашт.",
}

TAB_ICONS = {
    TAB_HOME:         "assets/images/icons/tab_home.png",
    TAB_CLICK:        "assets/images/icons/tab_click.png",
    TAB_WORKERS:      "assets/images/icons/tab_workers.png",
    TAB_REBIRTH:      "assets/images/icons/tab_rebirth.png",
    TAB_ACHIEVEMENTS: "assets/images/icons/tab_ach.png",
    TAB_STATS:        "assets/images/icons/tab_stats.png",
    TAB_SETTINGS:     "assets/images/icons/tab_settings.png",
}

COIN_RADIUS_RATIO = 0.28
COIN_GLOW_RATIO   = 0.36

CARD_H    = 82
CARD_MRG  = 8
CARD_PAD  = 12
ICON_SIZE = 54

ACH_COLS  = 4
ACH_ICON  = 68
ACH_PAD   = 10

SLIDER_H  = 20
BTN_H     = 54
BTN_R     = 10

TOGGLE_W  = 70
TOGGLE_H  = 34

PAD_EDGE  = 16   # типовий відступ від краю екрана
PAD_SM    = 10
PAD_XS    = 8

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
    COIN_IMAGE_TEMPLATE, COIN_CLICK_SQUASH, COLOR_BG_GLOW_ALPHA, COLOR_FALLING_COIN,
    FALLING_COIN_COUNT,
    MUSIC_FILE, UPGRADES, ACHIEVEMENTS, OFFLINE_INCOME_CAP, POPUP_LIFETIME, POPUP_SPEED,
    MAX_CLICKS_PER_SEC, REBIRTH_BASE_COST, COIN_ANIM_SPEED, COIN_BASE_RADIUS, COIN_GLOW_RADIUS,
)


def _sc(value: float, scale: float, minimum: int = 1) -> int:
    return max(minimum, int(round(value * scale)))


def apply_layout(screen_w: int, screen_h: int, density: float = 1.0) -> float:
    """Перераховує розміри UI під фактичний розмір екрана."""
    global SCALE, RES_BAR_H, TAB_BAR_H, TAB_BTN_W
    global CARD_H, CARD_MRG, CARD_PAD, ICON_SIZE
    global ACH_ICON, ACH_PAD, SLIDER_H, BTN_H, BTN_R
    global TOGGLE_W, TOGGLE_H, PAD_EDGE, PAD_SM, PAD_XS

    s = min(screen_w / DESIGN_W, screen_h / DESIGN_H)
    # На Android SDL часто створює буфер ~480×854, а density 2–3 — UI лишається дрібним.
    if density > 1.0:
        if screen_w <= int(DESIGN_W * 1.15) or screen_h <= int(DESIGN_H * 1.15):
            s = max(s, density)
    SCALE = s

    RES_BAR_H = _sc(80, s)
    TAB_BAR_H = _sc(72, s)
    TAB_BTN_W = max(screen_w // len(TABS_MOBILE), _sc(72, s))

    CARD_H    = _sc(82, s)
    CARD_MRG  = _sc(8, s)
    CARD_PAD  = _sc(12, s)
    ICON_SIZE = _sc(54, s)

    ACH_ICON  = _sc(68, s)
    ACH_PAD   = _sc(10, s)

    SLIDER_H  = _sc(20, s)
    BTN_H     = _sc(54, s)
    BTN_R     = _sc(10, s, 4)

    TOGGLE_W  = _sc(70, s)
    TOGGLE_H  = _sc(34, s)

    PAD_EDGE  = _sc(16, s)
    PAD_SM    = _sc(10, s)
    PAD_XS    = _sc(8, s)

    return s


def desktop_window_size(display_w: int, display_h: int) -> tuple[int, int]:
    """Початковий розмір вікна на ПК — великий portrait, не крихітний 480px."""
    h = min(int(display_h * 0.88), 1080)
    w = int(h * DESIGN_W / DESIGN_H)
    w = min(w, max(int(display_w * 0.5), 400))
    w = max(400, w)
    h = max(700, h)
    return w, h
