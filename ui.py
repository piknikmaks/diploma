# ─────────────────────────────────────────────
#  ui.py  —  весь рендеринг
#  Малює але не змінює ігровий стан
# ─────────────────────────────────────────────
import pygame
import math
import os

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TOP_BAR_HEIGHT, GAME_AREA_WIDTH, PANEL_WIDTH,
    TAB_BAR_HEIGHT, TAB_CLICK, TAB_WORKERS, TAB_SETTINGS, TABS,
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
    COIN_BASE_RADIUS, COIN_GLOW_RADIUS,
)


# ══════════════════════════════════════════════
#  Шрифти
# ══════════════════════════════════════════════
_fonts: dict = {}

def init_fonts():
    _fonts["huge"]   = pygame.font.SysFont("Arial", 46, bold=True)
    _fonts["large"]  = pygame.font.SysFont("Arial", 28, bold=True)
    _fonts["medium"] = pygame.font.SysFont("Arial", 20)
    _fonts["medbold"]= pygame.font.SysFont("Arial", 20, bold=True)
    _fonts["small"]  = pygame.font.SysFont("Arial", 16)
    _fonts["popup"]  = pygame.font.SysFont("Arial", 24, bold=True)
    _fonts["stat"]        = pygame.font.SysFont("Arial", 26, bold=True)
    _fonts["click_label"] = pygame.font.SysFont("Arial", 22, bold=True)

def _f(name): return _fonts[name]


# ══════════════════════════════════════════════
#  Кеш іконок
# ══════════════════════════════════════════════
_icon_cache: dict = {}
_coin_img = None        # assets/images/coin.png
_gem_img  = None        # assets/images/gem.png


def _load_image(path: str, size: tuple | None = None) -> pygame.Surface | None:
    """Завантажує зображення з диску (з кешем). Повертає None якщо файл не знайдено."""
    key = (path, size)
    if key in _icon_cache:
        return _icon_cache[key]
    if not os.path.exists(path):
        _icon_cache[key] = None
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _icon_cache[key] = img
        return img
    except Exception:
        _icon_cache[key] = None
        return None


def init_images():
    """Викликати після init_fonts(). Завантажує coin.png і gem.png."""
    global _coin_img, _gem_img
    _coin_img = _load_image("assets/images/coin.png", (38, 38))
    _gem_img  = _load_image("assets/images/gem.png",
                            (COIN_BASE_RADIUS * 2 - 20, COIN_BASE_RADIUS * 2 - 20))


# ══════════════════════════════════════════════
#  Базові хелпери малювання
# ══════════════════════════════════════════════
def _text(surface, text, font, color, x, y, anchor="topleft"):
    surf = _f(font).render(str(text), True, color)
    rect = surf.get_rect()
    setattr(rect, anchor, (x, y))
    surface.blit(surf, rect)
    return rect

def _rrect(surface, color, rect, r=8, border=None, bw=2):
    pygame.draw.rect(surface, color, rect, border_radius=r)
    if border:
        pygame.draw.rect(surface, border, rect, bw, border_radius=r)

def _fmt(n: float) -> str:
    if n < 1_000:        return str(int(n))
    elif n < 1_000_000:  return f"{n/1_000:.1f}K"
    elif n < 1_000_000_000: return f"{n/1_000_000:.1f}M"
    else:                return f"{n/1_000_000_000:.1f}B"


# ══════════════════════════════════════════════
#  Верхній бар (лічильник монет)
# ══════════════════════════════════════════════
def draw_top_bar(surface, game):
    bar = pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT)
    pygame.draw.rect(surface, COLOR_TOP_BAR, bar)
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (0, TOP_BAR_HEIGHT - 1), (WINDOW_WIDTH, TOP_BAR_HEIGHT - 1), 2)

    cx = GAME_AREA_WIDTH // 2
    cy = TOP_BAR_HEIGHT  // 2

    # число монет
    coins_str = _fmt(game.coins)
    coin_surf = _f("huge").render(coins_str, True, COLOR_COIN_VAL)
    coin_rect = coin_surf.get_rect(midright=(cx - 4, cy))
    surface.blit(coin_surf, coin_rect)

    # іконка монети (coin.png або жовте коло-заглушка)
    if _coin_img:
        img_rect = _coin_img.get_rect(midleft=(cx + 4, cy))
        surface.blit(_coin_img, img_rect)
    else:
        pygame.draw.circle(surface, (255, 200, 0), (cx + 24, cy), 18)
        pygame.draw.circle(surface, (200, 150, 0), (cx + 24, cy), 18, 3)
        _text(surface, "$", "small", (140, 100, 0), cx + 24, cy, anchor="center")


# ══════════════════════════════════════════════
#  Ліва зона кліку
# ══════════════════════════════════════════════
def draw_game_area(surface, game):
    area = pygame.Rect(0, TOP_BAR_HEIGHT, GAME_AREA_WIDTH,
                       WINDOW_HEIGHT - TOP_BAR_HEIGHT)
    pygame.draw.rect(surface, COLOR_BG, area)

    cx = GAME_AREA_WIDTH // 2
    cy = TOP_BAR_HEIGHT + (WINDOW_HEIGHT - TOP_BAR_HEIGHT) // 2 - 20

    _draw_gem(surface, cx, cy, game.coin_scale)

    # "Клік!" підпис
    _text(surface, "Клік!", "click_label", COLOR_TEXT_DIM,
          cx, cy + COIN_GLOW_RADIUS + 14, anchor="midtop")

    # CPS і CPC — між топ-баром і монетою, ближче до верху
    stat_y = TOP_BAR_HEIGHT + 18

    if game.coins_per_sec > 0:
        cps = f"+{_fmt(game.coins_per_sec)}/сек"
        _text(surface, cps, "stat", COLOR_PASSIVE,
              cx, stat_y, anchor="midtop")
        stat_y += 34

    cpc = f"{_fmt(game.coins_per_click)} за клік"
    _text(surface, cpc, "medium", COLOR_CPC,
          cx, stat_y, anchor="midtop")

    _draw_popups(surface, game.popups)


def _draw_gem(surface, cx, cy, scale):
    r_glow = int(COIN_GLOW_RADIUS * scale)
    r_base = int(COIN_BASE_RADIUS * scale)

    # ореол (синьо-фіолетовий градієнт через кілька кіл)
    glow_surf = pygame.Surface((r_glow * 2 + 4, r_glow * 2 + 4), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        alpha = int(30 * (i / 6))
        gr = r_base + int((r_glow - r_base) * (i / 6))
        pygame.draw.circle(glow_surf, (110, 100, 220, alpha),
                           (r_glow + 2, r_glow + 2), gr)
    surface.blit(glow_surf, (cx - r_glow - 2, cy - r_glow - 2))

    # зовнішнє кільце
    pygame.draw.circle(surface, (140, 130, 230), (cx, cy), r_base, 4)

    # якщо є gem.png — малюємо його, інакше заглушка
    if _gem_img:
        size = int((r_base - 10) * 2 * scale)
        img  = pygame.transform.smoothscale(_gem_img, (size, size))
        rect = img.get_rect(center=(cx, cy))
        surface.blit(img, rect)
    else:
        _draw_gem_fallback(surface, cx, cy, r_base)


def _draw_gem_fallback(surface, cx, cy, r):
    """Простий 8-бітний діамант з кількох полігонів."""
    s = int(r * 0.72)
    # корпус
    pts_top = [(cx, cy - s), (cx - s * 0.6, cy - s * 0.15),
               (cx + s * 0.6, cy - s * 0.15)]
    pts_bot = [(cx - s * 0.6, cy - s * 0.15), (cx, cy + s),
               (cx + s * 0.6, cy - s * 0.15)]
    pygame.draw.polygon(surface, (80, 200, 240),  [(int(x), int(y)) for x,y in pts_top])
    pygame.draw.polygon(surface, (50, 160, 210),  [(int(x), int(y)) for x,y in pts_bot])
    # блик
    pygame.draw.polygon(surface, (160, 230, 255),
                        [(cx, cy - s + 4), (cx - 10, cy - s * 0.15),
                         (cx + 4, cy - s * 0.15)])


def _draw_popups(surface, popups):
    for p in popups:
        text = f"+{_fmt(p.value)}"
        surf = _f("popup").render(text, True, COLOR_POPUP)
        surf.set_alpha(p.alpha)
        rect = surf.get_rect(center=(int(p.x), int(p.y)))
        surface.blit(surf, rect)


# ══════════════════════════════════════════════
#  Права панель з вкладками
# ══════════════════════════════════════════════

# Прямокутники вкладок та кнопок апгрейдів (для hit-test)
_tab_rects:     list[pygame.Rect] = []
_upgrade_rects: list              = []   # list of (Rect, upgrade_id)
_toggle_rects:  dict              = {}   # {"sound": Rect, "music": Rect}
_delete_rect:   pygame.Rect | None = None
_confirm_rect:  pygame.Rect | None = None
_confirm_mode:  bool = False            # чи показуємо підтвердження

# Скрол апгрейдів — окремо для кожної вкладки
_scroll: dict = {"click": 0, "worker": 0}
_SCROLL_SPEED = 30   # px за одиницю колеса


def draw_panel(surface, game, current_tab: str):
    px = GAME_AREA_WIDTH
    panel_rect = pygame.Rect(px, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect)
    pygame.draw.line(surface, COLOR_PANEL_BORDER,
                     (px, 0), (px, WINDOW_HEIGHT), 2)

    _draw_tab_bar(surface, px, current_tab)

    content_top = TOP_BAR_HEIGHT + TAB_BAR_HEIGHT
    if current_tab == TAB_CLICK:
        _draw_upgrades(surface, px, content_top, game, "click")
    elif current_tab == TAB_WORKERS:
        _draw_upgrades(surface, px, content_top, game, "worker")
    elif current_tab == TAB_SETTINGS:
        _draw_settings(surface, px, content_top, game)


# ── Рядок вкладок ─────────────────────────────
_TAB_ICONS = {
    TAB_CLICK:    ("assets/images/icons/tab_click.png",    "⚒"),
    TAB_WORKERS:  ("assets/images/icons/tab_workers.png",  "👷"),
    TAB_SETTINGS: ("assets/images/icons/tab_settings.png", "⚙"),
}

def _draw_tab_bar(surface, px, current_tab):
    global _tab_rects
    _tab_rects.clear()

    bar_y  = TOP_BAR_HEIGHT
    tab_w  = PANEL_WIDTH // len(TABS)
    pad    = 8

    # фон рядка вкладок (злитий з топ-баром)
    pygame.draw.rect(surface, COLOR_TOP_BAR,
                     (px, bar_y, PANEL_WIDTH, TAB_BAR_HEIGHT))
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (px, bar_y + TAB_BAR_HEIGHT - 1),
                     (px + PANEL_WIDTH, bar_y + TAB_BAR_HEIGHT - 1), 2)

    mx, my = pygame.mouse.get_pos()

    for i, tab in enumerate(TABS):
        tx = px + i * tab_w
        rect = pygame.Rect(tx + pad // 2, bar_y + pad // 2,
                           tab_w - pad, TAB_BAR_HEIGHT - pad)
        _tab_rects.append(rect)

        active  = (tab == current_tab)
        hovered = rect.collidepoint(mx, my) and not active

        bg = COLOR_TAB_ACTIVE if active else (COLOR_TAB_HOVER if hovered else COLOR_TAB_INACTIVE)
        bw = 2 if active else 1
        _rrect(surface, bg, rect, r=8, border=COLOR_TAB_BORDER, bw=bw)

        # іконка вкладки
        icon_path, fallback = _TAB_ICONS[tab]
        img = _load_image(icon_path, (36, 36))
        if img:
            ir = img.get_rect(center=rect.center)
            surface.blit(img, ir)
        else:
            _text(surface, fallback, "large", COLOR_TEXT,
                  rect.centerx, rect.centery, anchor="center")


# ── Список апгрейдів ──────────────────────────
_BTN_H   = 78
_BTN_MRG = 8
_BTN_PAD = 12

def _draw_upgrades(surface, px, top_y, game, upg_type: str):
    global _upgrade_rects
    _upgrade_rects.clear()

    mx, my = pygame.mouse.get_pos()
    upgrades = [u for u in game.upgrades if u.type == upg_type]

    scroll_offset = _scroll.get(upg_type, 0)

    # Clip — малюємо тільки всередині контентної зони
    clip_rect = pygame.Rect(px, top_y, PANEL_WIDTH, WINDOW_HEIGHT - top_y)
    prev_clip  = surface.get_clip()
    surface.set_clip(clip_rect)

    for idx, upg in enumerate(upgrades):
        x    = px + _BTN_PAD
        y    = top_y + _BTN_PAD + idx * (_BTN_H + _BTN_MRG) - scroll_offset
        w    = PANEL_WIDTH - _BTN_PAD * 2
        rect = pygame.Rect(x, y, w, _BTN_H)

        # не малюємо і не додаємо до hit-test якщо повністю поза зоною
        if y + _BTN_H <= top_y or y >= WINDOW_HEIGHT:
            continue

        _upgrade_rects.append((rect, upg.id))
        can_afford = game.coins >= upg.current_cost
        hovered    = rect.collidepoint(mx, my)

        if can_afford:
            bg  = COLOR_BTN_HOVER   if hovered else COLOR_BTN_NORMAL
            brd = COLOR_BTN_BORDER_HOV if hovered else COLOR_BTN_BORDER
        else:
            bg  = COLOR_BTN_LOCKED
            brd = COLOR_BTN_BORDER

        _rrect(surface, bg, rect, r=8, border=brd, bw=2)

        # іконка
        icon_size = 54
        icon_rect = pygame.Rect(x + 10, y + (_BTN_H - icon_size) // 2,
                                icon_size, icon_size)
        img = _load_image(upg.icon_path, (icon_size, icon_size)) if upg.icon_path else None
        if img:
            surface.blit(img, icon_rect)
        else:
            _rrect(surface, (170, 170, 190), icon_rect, r=6,
                   border=COLOR_BTN_BORDER, bw=1)
            _text(surface, upg.name[0].upper(), "medbold",
                  COLOR_TEXT_DIM, icon_rect.centerx, icon_rect.centery, anchor="center")

        # текст
        txt_x = icon_rect.right + 10
        txt_y = y + 12

        name_col = COLOR_TEXT if can_afford else COLOR_TEXT_LOCKED
        _text(surface, upg.name,        "medbold", name_col, txt_x, txt_y)
        _text(surface, upg.description, "small",   COLOR_TEXT_DIM, txt_x, txt_y + 22)

        # ціна + іконка монети
        cost_col = (180, 130, 0) if can_afford else (160, 100, 100)
        cost_str = _fmt(upg.current_cost)

        if _coin_img:
            ci = pygame.transform.smoothscale(_coin_img, (20, 20))
            surface.blit(ci, (txt_x, txt_y + 44))
            _text(surface, cost_str, "small", cost_col, txt_x + 24, txt_y + 44)
        else:
            _text(surface, f"$ {cost_str}", "small", cost_col, txt_x, txt_y + 44)

        # рівень (праворуч)
        if upg.level > 0:
            _text(surface, f"Рвн.{upg.level}", "small", COLOR_PASSIVE,
                  rect.right - 10, y + 10, anchor="topright")

    surface.set_clip(prev_clip)   # скидаємо clip

    # скролбар (тільки якщо контент не вміщається)
    total_h = len(upgrades) * (_BTN_H + _BTN_MRG) + _BTN_PAD
    visible_h = WINDOW_HEIGHT - top_y
    if total_h > visible_h:
        _draw_scrollbar(surface, px, top_y, visible_h, total_h, scroll_offset)


def _draw_scrollbar(surface, px, top_y, visible_h, total_h, offset):
    bar_w = 6
    bar_x = px + PANEL_WIDTH - bar_w - 4
    ratio     = visible_h / total_h
    thumb_h   = max(30, int(visible_h * ratio))
    thumb_y   = top_y + int((offset / (total_h - visible_h)) * (visible_h - thumb_h))
    pygame.draw.rect(surface, (180, 180, 180),
                     (bar_x, top_y, bar_w, visible_h), border_radius=3)
    pygame.draw.rect(surface, (110, 110, 130),
                     (bar_x, thumb_y, bar_w, thumb_h), border_radius=3)


# ── Вкладка налаштувань ───────────────────────
_TOGGLE_W, _TOGGLE_H = 80, 36

def _draw_settings(surface, px, top_y, game):
    global _toggle_rects, _delete_rect, _confirm_rect

    _toggle_rects.clear()
    _delete_rect   = None
    _confirm_rect  = None

    title_y = top_y + 24
    _text(surface, "Налаштування", "large", COLOR_TEXT,
          px + PANEL_WIDTH // 2, title_y, anchor="midtop")

    rows = [
        ("sound", "Звуки монети",  game.sound_on),
        ("music", "Музика",        game.music_on),
    ]

    for i, (key, label, state) in enumerate(rows):
        row_y  = title_y + 70 + i * 64
        row_cx = px + PANEL_WIDTH // 2

        # підпис
        _text(surface, label, "medium", COLOR_TEXT,
              row_cx - _TOGGLE_W // 2 - 10, row_y + 4, anchor="midright")

        # тогл
        tog_rect = pygame.Rect(row_cx - _TOGGLE_W // 2,
                               row_y, _TOGGLE_W, _TOGGLE_H)
        _toggle_rects[key] = tog_rect
        _draw_toggle(surface, tog_rect, state)

    # ── Кнопка видалення прогресу ─────────────
    del_y  = title_y + 70 + len(rows) * 64 + 24
    del_w  = PANEL_WIDTH - 48
    del_h  = 44
    del_x  = px + 24
    _delete_rect = pygame.Rect(del_x, del_y, del_w, del_h)

    if _confirm_mode:
        # ── режим підтвердження ──
        _rrect(surface, (240, 240, 240), _delete_rect, r=8,
               border=(180, 180, 180), bw=2)
        _text(surface, "Ви впевнені?", "medbold", (80, 80, 80),
              _delete_rect.centerx, _delete_rect.centery - 10, anchor="center")

        # дві кнопки: ТАК / НІ
        half_w = (del_w - 12) // 2
        yes_rect = pygame.Rect(del_x,              del_y + del_h + 8, half_w, 40)
        no_rect  = pygame.Rect(del_x + half_w + 12, del_y + del_h + 8, half_w, 40)

        _rrect(surface, COLOR_DELETE_CONFIRM, yes_rect, r=8)
        _text(surface, "Видалити", "medbold", COLOR_DELETE_TEXT,
              yes_rect.centerx, yes_rect.centery, anchor="center")

        _rrect(surface, (160, 160, 160), no_rect, r=8)
        _text(surface, "Скасувати", "medbold", COLOR_DELETE_TEXT,
              no_rect.centerx, no_rect.centery, anchor="center")

        _confirm_rect = (yes_rect, no_rect)
    else:
        # ── звичайна кнопка ──
        mx, my = pygame.mouse.get_pos()
        hov = _delete_rect.collidepoint(mx, my)
        bg  = COLOR_DELETE_CONFIRM if hov else COLOR_DELETE_BTN
        _rrect(surface, bg, _delete_rect, r=8)
        _text(surface, "Видалити прогрес", "medbold", COLOR_DELETE_TEXT,
              _delete_rect.centerx, _delete_rect.centery, anchor="center")

    # підказка
    _text(surface, "S — зберегти гру", "small", COLOR_TEXT_DIM,
          px + PANEL_WIDTH // 2, WINDOW_HEIGHT - 30, anchor="midbottom")


def _draw_toggle(surface, rect, state: bool):
    bg = COLOR_TOGGLE_ON if state else COLOR_TOGGLE_OFF
    pygame.draw.rect(surface, bg, rect, border_radius=_TOGGLE_H // 2)

    # кулька
    margin = 3
    knob_r = _TOGGLE_H // 2 - margin
    knob_x = rect.right - knob_r - margin if state else rect.left + knob_r + margin
    knob_y = rect.centery
    pygame.draw.circle(surface, COLOR_TOGGLE_KNOB, (knob_x, knob_y), knob_r)

    # текст ON/OFF
    label = "ON" if state else "OFF"
    label_x = rect.left + 8 if state else rect.right - 8
    anchor  = "midleft" if state else "midright"
    col = (255, 255, 255) if state else (120, 120, 120)
    _text(surface, label, "small", col, label_x, rect.centery, anchor=anchor)


# ══════════════════════════════════════════════
#  Hit-test функції (для main.py)
# ══════════════════════════════════════════════
def get_clicked_tab(mx, my) -> str | None:
    for i, rect in enumerate(_tab_rects):
        if rect.collidepoint(mx, my):
            return TABS[i]
    return None


def get_clicked_upgrade(mx, my) -> str | None:
    for rect, uid in _upgrade_rects:
        if rect.collidepoint(mx, my):
            return uid
    return None


def get_clicked_toggle(mx, my) -> str | None:
    for key, rect in _toggle_rects.items():
        if rect.collidepoint(mx, my):
            return key
    return None


def get_clicked_delete(mx, my) -> str | None:
    """
    Повертає:
      'delete'  — клік по кнопці «Видалити прогрес»
      'yes'     — підтвердження видалення
      'no'      — скасування
      None      — нічого
    """
    global _confirm_mode
    if _confirm_mode and _confirm_rect:
        yes_rect, no_rect = _confirm_rect
        if yes_rect.collidepoint(mx, my): return 'yes'
        if no_rect.collidepoint(mx, my):  return 'no'
        return None
    if _delete_rect and _delete_rect.collidepoint(mx, my):
        return 'delete'
    return None


def set_confirm_mode(val: bool):
    global _confirm_mode
    _confirm_mode = val


def scroll_upgrades(tab: str, delta: int):
    """Прокручує список апгрейдів. delta > 0 — вниз, < 0 — вгору."""
    if tab not in _scroll:
        return
    _scroll[tab] = max(0, _scroll[tab] + delta * _SCROLL_SPEED)


def get_coin_center() -> tuple[int, int]:
    cx = GAME_AREA_WIDTH // 2
    cy = TOP_BAR_HEIGHT + (WINDOW_HEIGHT - TOP_BAR_HEIGHT) // 2 - 20
    return cx, cy


# ══════════════════════════════════════════════
#  Офлайн-банер
# ══════════════════════════════════════════════
_offline_msg:   str   = ""
_offline_timer: float = 0.0
OFFLINE_MSG_DURATION  = 4.0


def show_offline_message(earned: float, format_fn):
    global _offline_msg, _offline_timer
    if earned > 0:
        _offline_msg   = f"Поки вас не було: +{format_fn(earned)} монет!"
        _offline_timer = OFFLINE_MSG_DURATION


def draw_offline_message(surface, dt: float):
    global _offline_timer
    if _offline_timer <= 0:
        return
    _offline_timer -= dt
    alpha = min(255, int(255 * (_offline_timer / OFFLINE_MSG_DURATION) * 2))
    surf  = _f("medium").render(_offline_msg, True, COLOR_PASSIVE)
    surf.set_alpha(alpha)
    rect  = surf.get_rect(center=(GAME_AREA_WIDTH // 2, WINDOW_HEIGHT - 36))
    surface.blit(surf, rect)