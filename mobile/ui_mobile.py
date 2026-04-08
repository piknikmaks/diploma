# ─────────────────────────────────────────────
#  ui_mobile.py  —  увесь рендеринг мобільної версії
#  Малює, але не змінює ігровий стан.
# ─────────────────────────────────────────────
import pygame
import math
import os, sys
import random

from settings_mobile import (
    RES_BAR_H, TAB_BAR_H, TAB_BTN_W,
    TABS_MOBILE, TAB_LABELS, TAB_ICONS,
    TAB_HOME, TAB_CLICK, TAB_WORKERS, TAB_REBIRTH,
    TAB_ACHIEVEMENTS, TAB_STATS, TAB_SETTINGS,
    COIN_RADIUS_RATIO, COIN_GLOW_RATIO,
    CARD_H, CARD_MRG, CARD_PAD, ICON_SIZE,
    ACH_COLS, ACH_ICON, ACH_PAD,
    SLIDER_H, BTN_H, BTN_R,
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
    COIN_BASE_RADIUS, COIN_GLOW_RADIUS,
)


# ══════════════════════════════════════════════
#  Глобальний розмір екрану (встановлюється при init)
# ══════════════════════════════════════════════
W: int = 480
H: int = 854

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def set_screen_size(w: int, h: int):
    """Викликати одразу після pygame.display.set_mode()."""
    global W, H
    W, H = w, h


def content_top() -> int:
    """Y-початок контентної зони (нижче бару ресурсів)."""
    return RES_BAR_H


def content_bottom() -> int:
    """Y-кінець контентної зони (вище бару вкладок)."""
    return H - TAB_BAR_H


def content_h() -> int:
    return content_bottom() - content_top()


def coin_radius() -> int:
    return int(W * COIN_RADIUS_RATIO)


def coin_glow() -> int:
    return int(W * COIN_GLOW_RATIO)


# ══════════════════════════════════════════════
#  Шрифти
# ══════════════════════════════════════════════
_fonts: dict = {}


def init_fonts():
    """Завантажує шрифти. Розміри адаптовані під мобільний екран."""
    _fonts["huge"]      = pygame.font.SysFont("Arial", 40, bold=True)
    _fonts["large"]     = pygame.font.SysFont("Arial", 26, bold=True)
    _fonts["stat"]      = pygame.font.SysFont("Arial", 22, bold=True)
    _fonts["medium"]    = pygame.font.SysFont("Arial", 18)
    _fonts["medbold"]   = pygame.font.SysFont("Arial", 18, bold=True)
    _fonts["small"]     = pygame.font.SysFont("Arial", 14)
    _fonts["smallbold"] = pygame.font.SysFont("Arial", 14, bold=True)
    _fonts["popup"]     = pygame.font.SysFont("Arial", 22, bold=True)
    _fonts["tab"]       = pygame.font.SysFont("Arial", 12, bold=True)
    _fonts["victory"]   = pygame.font.SysFont("Arial", 52, bold=True)


def _f(name: str) -> pygame.font.Font:
    return _fonts[name]


# ══════════════════════════════════════════════
#  Кеш зображень
# ══════════════════════════════════════════════
_icon_cache: dict = {}
_coin_img         = None   # іконка монети у барі ресурсів
_gem_imgs: dict   = {}     # зображення монети за рівнем перерождення


def _load_image(path: str, size=None):
    """Завантажує зображення з кешем. Повертає None якщо файл відсутній."""
    key = (path, size)
    if key in _icon_cache:
        return _icon_cache[key]
    if not os.path.exists(resource_path(path)):
        _icon_cache[key] = None
        return None
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _icon_cache[key] = img
        return img
    except Exception:
        _icon_cache[key] = None
        return None


def init_images():
    """Завантажує базові зображення. Викликати після init_fonts()."""
    global _coin_img
    _coin_img = _load_image("assets/images/coin.png", (34, 34))


def _get_gem(rebirth_count: int):
    """Повертає зображення монети для поточного рівня перерождення."""
    if rebirth_count not in _gem_imgs:
        r = coin_radius()
        sz  = (r * 2 - 16, r * 2 - 16)
        img = _load_image(COIN_IMAGE_TEMPLATE.format(rebirth_count), sz)
        if img is None:
            for i in range(rebirth_count - 1, -1, -1):
                img = _load_image(COIN_IMAGE_TEMPLATE.format(i), sz)
                if img:
                    break
        _gem_imgs[rebirth_count] = img
    return _gem_imgs[rebirth_count]


# ══════════════════════════════════════════════
#  Базові хелпери малювання
# ══════════════════════════════════════════════
def _txt(surface, text: str, font: str, color, x: int, y: int, anchor="topleft"):
    """Малює текст з вибором точки прив'язки."""
    surf = _f(font).render(str(text), True, color)
    rect = surf.get_rect()
    setattr(rect, anchor, (x, y))
    surface.blit(surf, rect)
    return rect


def _rrect(surface, color, rect, r=8, border=None, bw=2):
    """Малює прямокутник з заокругленими кутами і опційною рамкою."""
    pygame.draw.rect(surface, color, rect, border_radius=r)
    if border:
        pygame.draw.rect(surface, border, rect, bw, border_radius=r)


def _fmt(n: float) -> str:
    """Форматує велике число: 1500 -> '1.5K' тощо."""
    if n < 1_000:    return str(int(n))
    elif n < 1e6:    return f"{n/1_000:.1f}K"
    elif n < 1e9:    return f"{n/1e6:.1f}M"
    elif n < 1e12:   return f"{n/1e9:.1f}B"
    else:            return f"{n/1e12:.1f}T"


def _divider(surface, y: int, pad: int = 16):
    """Малює горизонтальний роздільник."""
    pygame.draw.line(surface, COLOR_PANEL_BORDER,
                     (pad, y), (W - pad, y), 1)


# ══════════════════════════════════════════════
#  Верхній бар ресурсів (незмінний між вкладками)
# ══════════════════════════════════════════════
def draw_res_bar(surface, game):
    """
    Малює бар ресурсів зверху: монети | монет/сек | за клік.
    Завжди видимий незалежно від поточної вкладки.
    """
    pygame.draw.rect(surface, COLOR_TOP_BAR, (0, 0, W, RES_BAR_H))
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (0, RES_BAR_H - 1), (W, RES_BAR_H - 1), 2)

    cx = W // 2
    cy = RES_BAR_H // 2

    # -- Монети (центр) --
    coins_surf = _f("huge").render(_fmt(game.coins), True, COLOR_COIN_VAL)
    coins_rect = coins_surf.get_rect(midright=(cx - 2, cy))
    surface.blit(coins_surf, coins_rect)

    # -- Іконка монети --
    if _coin_img:
        surface.blit(_coin_img, _coin_img.get_rect(midleft=(cx + 2, cy)))
    else:
        pygame.draw.circle(surface, (255, 200, 0), (cx + 20, cy), 16)
        pygame.draw.circle(surface, (200, 150, 0), (cx + 20, cy), 16, 2)

    # -- Монет/сек (ліворуч) --
    if game.coins_per_sec > 0:
        cps_str = f"+{_fmt(game.coins_per_sec)}/c"
        _txt(surface, cps_str, "small", COLOR_PASSIVE, 10, cy, anchor="midleft")

    # -- За клік (праворуч) --
    cpc_str = f"{_fmt(game.coins_per_click)}/клік"
    _txt(surface, cpc_str, "small", COLOR_CPC, W - 10, cy, anchor="midright")

    # -- Множник перерождення (якщо є) --
    if game.rebirth_count > 0:
        mult = f"x{int(game.rebirth_multiplier)}"
        _txt(surface, mult, "smallbold", COLOR_REBIRTH_GLOW,
             W // 2, 4, anchor="midtop")


# ══════════════════════════════════════════════
#  Нижній бар вкладок (горизонтально прокручуваний)
# ══════════════════════════════════════════════
_tab_scroll_x: float = 0.0   # зміщення прокручування бару вкладок
_tab_rects: list     = []     # список (Rect, tab_id) для hit-test


def draw_tab_bar(surface, current_tab: str):
    """Малює прокручуваний рядок вкладок знизу екрану."""
    global _tab_rects
    _tab_rects.clear()

    bar_y = H - TAB_BAR_H
    pygame.draw.rect(surface, COLOR_TOP_BAR, (0, bar_y, W, TAB_BAR_H))
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (0, bar_y), (W, bar_y), 2)

    pad = 6
    clip_prev = surface.get_clip()
    surface.set_clip(pygame.Rect(0, bar_y, W, TAB_BAR_H))

    for i, tab in enumerate(TABS_MOBILE):
        tx   = int(i * TAB_BTN_W - _tab_scroll_x)
        rect = pygame.Rect(tx + pad // 2, bar_y + pad // 2,
                           TAB_BTN_W - pad, TAB_BAR_H - pad)

        # хітбокс зберігаємо з реальними координатами
        hit_rect = pygame.Rect(tx, bar_y, TAB_BTN_W, TAB_BAR_H)
        _tab_rects.append((hit_rect, tab))

        # малюємо тільки видимі кнопки
        if tx + TAB_BTN_W < 0 or tx > W:
            continue

        active = (tab == current_tab)
        bg     = COLOR_TAB_ACTIVE if active else COLOR_TAB_INACTIVE
        _rrect(surface, bg, rect, r=8,
               border=COLOR_TAB_BORDER, bw=2 if active else 1)

        # іконка
        icon_path = TAB_ICONS.get(tab, "")
        img = _load_image(icon_path, (28, 28)) if icon_path else None
        if img:
            ir = img.get_rect(center=(rect.centerx, rect.top + 20))
            surface.blit(img, ir)
            # підпис під іконкою
            label_y = rect.top + 34
        else:
            label_y = rect.centery - 6

        _txt(surface, TAB_LABELS.get(tab, tab), "tab", COLOR_TEXT,
             rect.centerx, label_y, anchor="midtop")

    surface.set_clip(clip_prev)


def get_tab_at(x: int, y: int):
    """Повертає tab_id якщо торкнулись кнопки вкладки, інакше None."""
    for rect, tab in _tab_rects:
        if rect.collidepoint(x, y):
            return tab
    return None


def scroll_tab_bar(dx: float):
    """
    Зміщує прокручування бару вкладок на dx пікселів.
    dx > 0 — прокрутка вправо (бачимо праві вкладки).
    """
    global _tab_scroll_x
    total_w = len(TABS_MOBILE) * TAB_BTN_W
    max_scroll = max(0, total_w - W)
    _tab_scroll_x = max(0.0, min(float(max_scroll), _tab_scroll_x + dx))


# ══════════════════════════════════════════════
#  Головна вкладка (монета для кліку)
# ══════════════════════════════════════════════
def draw_home(surface, game):
    """Малює головний екран: монета по центру, спливаючі числа."""
    ct = content_top()
    ch = content_h()

    # фон
    pygame.draw.rect(surface, COLOR_BG, (0, ct, W, ch))

    cx  = W // 2
    cy  = ct + ch // 2

    _draw_gem(surface, cx, cy, game.coin_scale, game.rebirth_count)

    # підпис "Клік!"
    _txt(surface, "Клік!", "medbold", COLOR_TEXT_DIM,
         cx, cy + coin_glow() + 12, anchor="midtop")

    # спливаючі числа
    _draw_popups(surface, game.popups)

    # банер нового досягнення
    if game.new_achievement:
        _draw_ach_banner(surface, game)

def get_gem_image(rebirth_count):
    if rebirth_count not in _gem_imgs:
        size = (COIN_BASE_RADIUS * 2 - 20, COIN_BASE_RADIUS * 2 - 20)
        img  = _load_image(COIN_IMAGE_TEMPLATE.format(rebirth_count), size)
        if img is None:
            for r in range(rebirth_count - 1, -1, -1):
                img = _load_image(COIN_IMAGE_TEMPLATE.format(r), size)
                if img: break
        _gem_imgs[rebirth_count] = img
    return _gem_imgs[rebirth_count]

def _glow_colors():
    return [(110,100,220),(220,100,100),(100,200,100),(220,180,50),(50,200,220),(220,80,220)]

def _draw_gem(surface, cx, cy, scale, rb=0):
    r_glow = int(COIN_GLOW_RADIUS * scale)
    r_base = int(COIN_BASE_RADIUS * scale)
    cols = _glow_colors()
    gc   = cols[min(rb, len(cols)-1)]
    
    gsurf = pygame.Surface((r_glow*2+4, r_glow*2+4), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        alpha = int(30*(i/6))
        gr = r_base + int((r_glow-r_base)*(i/6))
        pygame.draw.circle(gsurf, (*gc, alpha), (r_glow+2, r_glow+2), gr)
    surface.blit(gsurf, (cx-r_glow-2, cy-r_glow-2))
    
    gem = get_gem_image(rb)
    if gem:
        sz  = int((r_base-10)*2*scale)
        img = pygame.transform.smoothscale(gem, (sz, sz))
        surface.blit(img, img.get_rect(center=(cx,cy)))
    else:
        pygame.draw.circle(surface, gc, (cx,cy), r_base, 4)
        
        fallback_colors = [((80,200,240),(50,160,210)),((240,100,100),(200,60,60)),
                           ((100,220,100),(60,170,60)),((240,200,60),(200,160,20)),
                           ((60,220,240),(20,160,200)),((220,80,220),(170,40,170))]
        c1, c2 = fallback_colors[min(rb, len(fallback_colors)-1)]
        s = int(r_base*0.72)
        t = [(cx,cy-s),(cx-s*0.6,cy-s*0.15),(cx+s*0.6,cy-s*0.15)]
        b = [(cx-s*0.6,cy-s*0.15),(cx,cy+s),(cx+s*0.6,cy-s*0.15)]
        pygame.draw.polygon(surface, c1, [(int(x),int(y)) for x,y in t])
        pygame.draw.polygon(surface, c2, [(int(x),int(y)) for x,y in b])


def _draw_popups(surface, popups):
    """Малює спливаючі числа (+N) над монетою."""
    for p in popups:
        surf = _f("popup").render(f"+{_fmt(p.value)}", True, COLOR_POPUP)
        surf.set_alpha(p.alpha)
        surface.blit(surf, surf.get_rect(center=(int(p.x), int(p.y))))


def get_coin_hit(game) -> tuple[int, int, int]:
    """Повертає (cx, cy, radius) хітбоксу монети."""
    ct  = content_top()
    ch  = content_h()
    cx  = W // 2
    cy  = ct + ch // 2
    rad = int(coin_glow() * game.coin_scale)
    return cx, cy, rad


# ══════════════════════════════════════════════
#  Банер нового досягнення
# ══════════════════════════════════════════════
_ach_banner_timer: float = 0.0
_ACH_BANNER_DUR   = 3.5


def tick_achievement_banner(game, dt: float):
    """Оновлює таймер банера. Викликати з main щокадру."""
    global _ach_banner_timer
    if _ach_banner_timer > 0:
        _ach_banner_timer -= dt
        if _ach_banner_timer <= 0:
            game.new_achievement = None


def _draw_ach_banner(surface, game):
    global _ach_banner_timer
    if game.new_achievement and _ach_banner_timer <= 0:
        _ach_banner_timer = _ACH_BANNER_DUR
    if _ach_banner_timer <= 0 or not game.new_achievement:
        return

    ach = game.new_achievement
    bw, bh = W - 40, 52
    bx, by = 20, H - TAB_BAR_H - bh - 10

    alpha  = min(255, int(255 * min(1.0, _ach_banner_timer)))
    banner = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(banner, (255, 215, 0, min(200, alpha)), (0, 0, bw, bh), border_radius=10)
    pygame.draw.rect(banner, (200, 160, 0, 255), (0, 0, bw, bh), 2, border_radius=10)
    surface.blit(banner, (bx, by))
    _txt(surface, "Досягнення!", "smallbold", (100, 70, 0), bx + bw // 2, by + 6,  anchor="midtop")
    _txt(surface, ach.name,      "medbold",   (60,  40, 0), bx + bw // 2, by + 26, anchor="midtop")


# ══════════════════════════════════════════════
#  Вкладки з апгрейдами (click / workers)
# ══════════════════════════════════════════════
_upg_rects: list = []    # список (Rect, upgrade_id) для hit-test
_upg_scroll: dict = {"click": 0, "worker": 0}   # вертикальний скрол


def draw_upgrades(surface, game, upg_type: str):
    """Малює список апгрейдів із вертикальним скролом."""
    global _upg_rects
    _upg_rects.clear()

    ct = content_top()
    ch = content_h()
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, ct, W, ch))

    upgrades = [u for u in game.upgrades if u.type == upg_type]
    off      = _upg_scroll.get(upg_type, 0)

    clip = pygame.Rect(0, ct, W, ch)
    prev = surface.get_clip()
    surface.set_clip(clip)

    for i, upg in enumerate(upgrades):
        x    = CARD_PAD
        y    = ct + CARD_PAD + i * (CARD_H + CARD_MRG) - int(off)
        w    = W - CARD_PAD * 2
        rect = pygame.Rect(x, y, w, CARD_H)

        # пропускаємо невидимі
        if y + CARD_H <= ct or y >= H - TAB_BAR_H:
            continue

        _upg_rects.append((rect, upg.id))
        can = game.coins >= upg.current_cost

        bg  = COLOR_BTN_HOVER  if can else COLOR_BTN_LOCKED
        brd = COLOR_BTN_BORDER_HOV if can else COLOR_BTN_BORDER
        _rrect(surface, bg, rect, r=8, border=brd, bw=2)

        # іконка
        ir = pygame.Rect(x + 10, y + (CARD_H - ICON_SIZE) // 2, ICON_SIZE, ICON_SIZE)
        img = _load_image(upg.icon_path, (ICON_SIZE, ICON_SIZE)) if upg.icon_path else None
        if img:
            surface.blit(img, ir)
        else:
            _rrect(surface, (170, 170, 190), ir, r=6, border=COLOR_BTN_BORDER, bw=1)
            _txt(surface, upg.name[0].upper(), "medbold", COLOR_TEXT_DIM,
                 ir.centerx, ir.centery, anchor="center")

        # текст праворуч від іконки
        tx = ir.right + 10
        ty = y + 12
        name_col = COLOR_TEXT if can else COLOR_TEXT_LOCKED
        _txt(surface, upg.name, "medbold", name_col, tx, ty)
        _txt(surface, upg.description, "small", COLOR_TEXT_DIM, tx, ty + 22)

        # ціна
        cost_col = (180, 130, 0) if can else (160, 100, 100)
        cost_str = _fmt(upg.current_cost)
        if _coin_img:
            ci = pygame.transform.smoothscale(_coin_img, (18, 18))
            surface.blit(ci, (tx, ty + 44))
            _txt(surface, cost_str, "small", cost_col, tx + 22, ty + 44)
        else:
            _txt(surface, f"$ {cost_str}", "small", cost_col, tx, ty + 44)

        # рівень (праворуч)
        if upg.level > 0:
            _txt(surface, f"Рвн.{upg.level}", "small", COLOR_PASSIVE,
                 rect.right - 10, y + 10, anchor="topright")

    surface.set_clip(prev)

    # скролбар
    total_h = len(upgrades) * (CARD_H + CARD_MRG) + CARD_PAD
    if total_h > ch:
        _draw_scrollbar(surface, ct, ch, total_h, int(off))


def _draw_scrollbar(surface, top_y: int, vis_h: int,
                    total_h: int, off: int):
    """Малює тонкий вертикальний скролбар."""
    bw = 5; bx = W - bw - 3
    ratio   = vis_h / total_h
    thumb_h = max(24, int(vis_h * ratio))
    max_off = max(1, total_h - vis_h)
    ty      = top_y + int((min(off, max_off) / max_off) * (vis_h - thumb_h))
    pygame.draw.rect(surface, (180, 180, 180), (bx, top_y, bw, vis_h), border_radius=3)
    pygame.draw.rect(surface, (100, 100, 130), (bx, ty, bw, thumb_h), border_radius=3)


def get_upgrade_at(x: int, y: int):
    """Повертає upgrade_id за координатами торкання, або None."""
    for rect, uid in _upg_rects:
        if rect.collidepoint(x, y):
            return uid
    return None


def scroll_upgrades(upg_type: str, dy: float):
    """Вертикальний скрол списку апгрейдів."""
    _upg_scroll[upg_type] = max(0.0, _upg_scroll.get(upg_type, 0) + dy)


def clamp_upgrade_scroll(upg_type: str, game):
    """Обмежує скрол щоб не виходити за межі списку."""
    upgrades  = [u for u in game.upgrades if u.type == upg_type]
    total_h   = len(upgrades) * (CARD_H + CARD_MRG) + CARD_PAD
    vis_h     = content_h()
    max_off   = max(0, total_h - vis_h)
    _upg_scroll[upg_type] = min(_upg_scroll.get(upg_type, 0), float(max_off))


# ══════════════════════════════════════════════
#  Перерождення
# ══════════════════════════════════════════════
_rebirth_rect          = None
_endgame_rect          = None
_endgame_confirm_rects = None
_endgame_confirm_mode  = False


def draw_rebirth(surface, game):
    """Малює вкладку перерождень."""
    global _rebirth_rect, _endgame_rect, _endgame_confirm_rects
    _rebirth_rect = _endgame_rect = _endgame_confirm_rects = None

    ct  = content_top()
    ch  = content_h()
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, ct, W, ch))

    cx  = W // 2
    y   = ct + 18

    _txt(surface, "Перерождення", "large", COLOR_TEXT, cx, y, anchor="midtop");  y += 40
    _txt(surface, f"Кiлькiсть: {game.rebirth_count}", "medbold",
         COLOR_PASSIVE, cx, y, anchor="midtop");  y += 28
    _txt(surface, f"Множник: x{int(game.rebirth_multiplier)}", "medium",
         COLOR_TEXT_DIM, cx, y, anchor="midtop"); y += 28
    _divider(surface, y);  y += 14

    can      = game.can_rebirth()
    cost_col = (180, 130, 0) if can else (160, 100, 100)
    _txt(surface, "Наступне перерождення:", "medium", COLOR_TEXT_DIM,
         cx, y, anchor="midtop"); y += 26
    _txt(surface, f"Цiна: {_fmt(game.rebirth_cost)} монет", "medbold",
         cost_col, cx, y, anchor="midtop"); y += 24
    _txt(surface, f"Дасть множник x{int(game.rebirth_multiplier) * 2}", "medium",
         COLOR_TEXT_DIM, cx, y, anchor="midtop"); y += 24
    _txt(surface, "Монети i апгрейди скинуться!", "small",
         (180, 100, 0), cx, y, anchor="midtop"); y += 34

    # кнопка перерождення
    bx = CARD_PAD;  bw = W - CARD_PAD * 2;  bh = BTN_H
    _rebirth_rect = pygame.Rect(bx, y, bw, bh)
    bg = (COLOR_REBIRTH_BTN if can else COLOR_REBIRTH_LOCKED)
    _rrect(surface, bg, _rebirth_rect, r=BTN_R)
    _txt(surface, "Переродитися", "large",
         COLOR_REBIRTH_TEXT if can else COLOR_TEXT_LOCKED,
         cx, _rebirth_rect.centery, anchor="center")
    y += bh + 12

    # прогрес-бар
    ph = 14
    progress = min(1.0, game.coins / max(1, game.rebirth_cost))
    pygame.draw.rect(surface, (200, 200, 200), (bx, y, bw, ph), border_radius=7)
    if progress > 0:
        pygame.draw.rect(surface, COLOR_REBIRTH_BTN,
                         (bx, y, int(bw * progress), ph), border_radius=7)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bx, y, bw, ph), 2, border_radius=7)
    _txt(surface, f"{progress * 100:.1f}%", "small", COLOR_TEXT_DIM,
         cx, y + ph + 4, anchor="midtop")
    y += ph + 30

    # кнопка кінця гри (тільки якщо всі досягнення виконані)
    if game.all_achievements_unlocked:
        _divider(surface, y); y += 12
        _txt(surface, "Всi досягнення виконано!", "smallbold",
             (140, 100, 0), cx, y, anchor="midtop"); y += 24
        eg_can   = game.can_end_game()
        eg_col   = (180, 130, 0) if eg_can else (160, 100, 100)
        _txt(surface, f"Цiна фiналу: {_fmt(game.end_game_cost)}", "medium",
             eg_col, cx, y, anchor="midtop"); y += 30

        if _endgame_confirm_mode:
            _txt(surface, "Ви впевненi? Це завершить гру!", "smallbold",
                 (100, 50, 0), cx, y, anchor="midtop"); y += 28
            hw  = (bw - 12) // 2
            yes = pygame.Rect(bx,           y, hw, BTN_H)
            no  = pygame.Rect(bx + hw + 12, y, hw, BTN_H)
            _rrect(surface, (200, 160, 0), yes, r=BTN_R)
            _txt(surface, "Завершити!", "medbold", (60, 30, 0),
                 yes.centerx, yes.centery, anchor="center")
            _rrect(surface, (150, 150, 150), no, r=BTN_R)
            _txt(surface, "Скасувати", "medbold", (255, 255, 255),
                 no.centerx, no.centery, anchor="center")
            _endgame_confirm_rects = (yes, no)
        else:
            _endgame_rect = pygame.Rect(bx, y, bw, BTN_H)
            bg2 = (230, 180, 0) if eg_can else (190, 190, 190)
            _rrect(surface, bg2, _endgame_rect, r=BTN_R)
            _txt(surface, "Завершити гру", "large",
                 (60, 30, 0) if eg_can else COLOR_TEXT_LOCKED,
                 cx, _endgame_rect.centery, anchor="center")


def get_rebirth_hit(x: int, y: int) -> bool:
    return bool(_rebirth_rect and _rebirth_rect.collidepoint(x, y))


def get_endgame_hit(x: int, y: int) -> str | None:
    """Повертає 'endgame' / 'yes' / 'no' або None."""
    global _endgame_confirm_mode
    if _endgame_confirm_mode and _endgame_confirm_rects:
        yr, nr = _endgame_confirm_rects
        if yr.collidepoint(x, y): return "yes"
        if nr.collidepoint(x, y): return "no"
        return None
    if _endgame_rect and _endgame_rect.collidepoint(x, y):
        return "endgame"
    return None


def set_endgame_confirm(val: bool):
    global _endgame_confirm_mode
    _endgame_confirm_mode = val


# ══════════════════════════════════════════════
#  Досягнення
# ══════════════════════════════════════════════
def draw_achievements(surface, game):
    """Малює сітку досягнень."""
    ct = content_top(); ch = content_h()
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, ct, W, ch))

    cx = W // 2
    _txt(surface, "Досягнення", "large", COLOR_TEXT, cx, ct + 14, anchor="midtop")
    unlocked = sum(1 for a in game.achievements if a.unlocked)
    _txt(surface, f"{unlocked} / {len(game.achievements)}", "medium",
         COLOR_TEXT_DIM, cx, ct + 46, anchor="midtop")

    # сітка іконок
    total_icon_w = ACH_COLS * (ACH_ICON + ACH_PAD) - ACH_PAD
    sx  = (W - total_icon_w) // 2
    sy  = ct + 80
    mx2, my2 = pygame.mouse.get_pos()
    tooltip   = None

    for i, ach in enumerate(game.achievements):
        col = i % ACH_COLS
        row = i // ACH_COLS
        x   = sx + col * (ACH_ICON + ACH_PAD)
        y   = sy + row * (ACH_ICON + ACH_PAD + 4)
        rect = pygame.Rect(x, y, ACH_ICON, ACH_ICON)

        if y > H - TAB_BAR_H:
            break

        bg  = COLOR_ACH_UNLOCKED if ach.unlocked else COLOR_ACH_LOCKED
        brd = COLOR_ACH_BORDER_ON if ach.unlocked else COLOR_ACH_BORDER_OFF
        _rrect(surface, bg, rect, r=8, border=brd, bw=2 if ach.unlocked else 1)

        img = _load_image(ach.icon, (ACH_ICON - 16, ACH_ICON - 16)) if ach.icon else None
        if img:
            ir = img.get_rect(center=rect.center)
            if not ach.unlocked:
                dark = img.copy()
                dark.fill((0, 0, 0, 140), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(dark, ir)
            else:
                surface.blit(img, ir)
        else:
            sym = "+" if ach.unlocked else "?"
            col_ = (100, 70, 0) if ach.unlocked else COLOR_TEXT_LOCKED
            _txt(surface, sym, "medbold", col_, rect.centerx, rect.centery, anchor="center")

        if rect.collidepoint(mx2, my2):
            tooltip = (ach, rect)

    if tooltip:
        ach, rect = tooltip
        _draw_ach_tooltip(surface, ach, rect)


def _draw_ach_tooltip(surface, ach, anchor_rect):
    """Мале спливаюче вікно з описом досягнення."""
    tw, th = 200, 68
    tx = min(anchor_rect.right + 6, W - tw - 4)
    ty = max(content_top() + 4, anchor_rect.top - th // 2)
    bg = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.rect(bg, (40, 40, 40, 210), (0, 0, tw, th), border_radius=8)
    surface.blit(bg, (tx, ty))
    pygame.draw.rect(surface, (80, 80, 80), (tx, ty, tw, th), 1, border_radius=8)
    nc = (255, 215, 0) if ach.unlocked else (200, 200, 200)
    _txt(surface, ach.name, "medbold", nc, tx + 8, ty + 8)
    _txt(surface, ach.desc, "small", (200, 200, 200), tx + 8, ty + 28)
    sc = (100, 220, 100) if ach.unlocked else (160, 100, 100)
    status = "Отримано" if ach.unlocked else "Заблоковано"
    _txt(surface, status, "small", sc, tx + 8, ty + 48)


# ══════════════════════════════════════════════
#  Статистика
# ══════════════════════════════════════════════
def draw_stats(surface, game):
    """Малює таблицю статистики."""
    ct = content_top(); ch = content_h()
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, ct, W, ch))

    _txt(surface, "Статистика", "large", COLOR_TEXT, W // 2, ct + 14, anchor="midtop")

    rows = [
        ("Монет зараз",        _fmt(game.coins)),
        ("Всього зароблено",    _fmt(game.total_earned)),
        ("За клiк",             _fmt(game.coins_per_click)),
        ("За секунду",          _fmt(game.coins_per_sec)),
        ("Клiкiв зроблено",     f"{game.total_clicks:,}"),
        ("Переороджень",        str(game.rebirth_count)),
        ("Множник доходу",      f"x{int(game.rebirth_multiplier)}"),
        ("Час у грi",           game.format_time(game.total_play_time)),
        ("Досягнень вiдкрито",  f"{sum(1 for a in game.achievements if a.unlocked)} / {len(game.achievements)}"),
    ]

    y = ct + 54
    for label, val in rows:
        if y + 26 > H - TAB_BAR_H:
            break
        _txt(surface, label + ":", "small", COLOR_TEXT_DIM, 16, y)
        _txt(surface, val, "medbold", COLOR_TEXT, W - 16, y, anchor="topright")
        y += 28
        _divider(surface, y - 2)


# ══════════════════════════════════════════════
#  Налаштування
# ══════════════════════════════════════════════
_toggle_rects: dict = {}
_slider_rect        = None
_delete_rect        = None
_confirm_rect       = None
_confirm_mode       = False
_TOGGLE_W           = 70
_TOGGLE_H           = 34


def draw_settings(surface, game):
    """Малює вкладку налаштувань."""
    global _toggle_rects, _slider_rect, _delete_rect, _confirm_rect
    _toggle_rects.clear()
    _slider_rect = _delete_rect = _confirm_rect = None

    ct  = content_top(); ch = content_h()
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, ct, W, ch))

    cx = W // 2
    y  = ct + 20
    _txt(surface, "Налаштування", "large", COLOR_TEXT, cx, y, anchor="midtop"); y += 44

    # -- Звуки монети (тогл) --
    _txt(surface, "Звуки монети:", "medium", COLOR_TEXT, 16, y + 4)
    tog_r = pygame.Rect(W - _TOGGLE_W - 16, y, _TOGGLE_W, _TOGGLE_H)
    _toggle_rects["sound"] = tog_r
    _draw_toggle(surface, tog_r, game.sound_on)
    y += 54

    # -- Гучнiсть музики --
    _txt(surface, "Гучнiсть музики:", "medium", COLOR_TEXT, 16, y); y += 28
    sw = W - 32; sx = 16
    _slider_rect = pygame.Rect(sx, y, sw, SLIDER_H)
    _draw_vol_slider(surface, _slider_rect, game.music_volume)
    vol_str = f"{int(game.music_volume * 100)}%"
    _txt(surface, vol_str, "medbold", COLOR_TEXT, cx, y + SLIDER_H + 6, anchor="midtop")
    y += SLIDER_H + 36

    # -- Видалення прогресу --
    _delete_rect = pygame.Rect(16, y, W - 32, BTN_H)
    if _confirm_mode:
        _rrect(surface, (240, 240, 240), _delete_rect, r=BTN_R,
               border=(180, 180, 180), bw=2)
        _txt(surface, "Ви впевненi?", "medbold", (80, 80, 80),
             cx, _delete_rect.centery - 10, anchor="center")
        hw  = (W - 44) // 2
        yes = pygame.Rect(16,          y + BTN_H + 8, hw, BTN_H)
        no  = pygame.Rect(16 + hw + 12, y + BTN_H + 8, hw, BTN_H)
        _rrect(surface, COLOR_DELETE_CONFIRM, yes, r=BTN_R)
        _txt(surface, "Видалити", "medbold", COLOR_DELETE_TEXT,
             yes.centerx, yes.centery, anchor="center")
        _rrect(surface, (160, 160, 160), no, r=BTN_R)
        _txt(surface, "Скасувати", "medbold", COLOR_DELETE_TEXT,
             no.centerx, no.centery, anchor="center")
        _confirm_rect = (yes, no)
    else:
        _rrect(surface, COLOR_DELETE_BTN, _delete_rect, r=BTN_R)
        _txt(surface, "Видалити прогрес", "medbold", COLOR_DELETE_TEXT,
             cx, _delete_rect.centery, anchor="center")

    _txt(surface, "S - зберегти гру", "small", COLOR_TEXT_DIM,
         cx, H - TAB_BAR_H - 28, anchor="midtop")


def _draw_toggle(surface, rect, state: bool):
    """Малює тогл-перемикач ON/OFF."""
    bg = COLOR_TOGGLE_ON if state else COLOR_TOGGLE_OFF
    pygame.draw.rect(surface, bg, rect, border_radius=_TOGGLE_H // 2)
    m  = 3; kr = _TOGGLE_H // 2 - m
    kx = rect.right - kr - m if state else rect.left + kr + m
    pygame.draw.circle(surface, COLOR_TOGGLE_KNOB, (kx, rect.centery), kr)
    lbl = "ON" if state else "OFF"
    lx  = rect.left + 8 if state else rect.right - 8
    anc = "midleft" if state else "midright"
    col = (255, 255, 255) if state else (120, 120, 120)
    _txt(surface, lbl, "small", col, lx, rect.centery, anchor=anc)


def _draw_vol_slider(surface, rect, volume: float):
    """Малює слайдер гучностi."""
    pygame.draw.rect(surface, (190, 190, 190), rect, border_radius=SLIDER_H // 2)
    if volume > 0:
        fill = pygame.Rect(rect.x, rect.y, int(rect.w * volume), rect.h)
        pygame.draw.rect(surface, COLOR_TOGGLE_ON, fill, border_radius=SLIDER_H // 2)
    pygame.draw.rect(surface, (150, 150, 150), rect, 2, border_radius=SLIDER_H // 2)
    kx = rect.x + int(rect.w * volume)
    kx = max(rect.x + 12, min(rect.right - 12, kx))
    pygame.draw.circle(surface, (255, 255, 255), (kx, rect.centery), 12)
    pygame.draw.circle(surface, (120, 120, 120), (kx, rect.centery), 12, 2)


def get_toggle_hit(x: int, y: int):
    """Повертає назву тогла за координатами або None."""
    for key, rect in _toggle_rects.items():
        expanded = rect.inflate(10, 10)
        if expanded.collidepoint(x, y):
            return key
    return None


def get_delete_hit(x: int, y: int):
    """Повертає 'delete' / 'yes' / 'no' або None."""
    if _confirm_mode and _confirm_rect:
        yr, nr = _confirm_rect
        if yr.collidepoint(x, y): return "yes"
        if nr.collidepoint(x, y): return "no"
        return None
    if _delete_rect and _delete_rect.collidepoint(x, y):
        return "delete"
    return None


def is_on_slider(x: int, y: int) -> bool:
    if _slider_rect is None:
        return False
    return _slider_rect.inflate(0, 24).collidepoint(x, y)


def slider_volume_at(x: int) -> float | None:
    if _slider_rect is None:
        return None
    val = (x - _slider_rect.x) / max(1, _slider_rect.w)
    return max(0.0, min(1.0, val))


def set_confirm_mode(val: bool):
    global _confirm_mode
    _confirm_mode = val


# ══════════════════════════════════════════════
#  Кiнцева анiмацiя перемоги
# ══════════════════════════════════════════════
_particles: list = []
_end_quit_rect = None
_end_cont_rect = None


def start_end_animation():
    """Запускає феєрверк частинок по центру екрану."""
    global _particles
    cx = W // 2; cy = H // 2
    _particles.clear()
    for _ in range(180):
        import math as _m
        angle = __import__("random").uniform(0, _m.tau)
        speed = __import__("random").uniform(60, 360)
        color = __import__("random").choice([
            (255, 215, 0), (255, 180, 0), (255, 100, 0),
            (255, 255, 100), (100, 220, 255), (220, 100, 255),
        ])
        size = __import__("random").randint(4, 10)
        life = __import__("random").uniform(1.5, 3.5)
        _particles.append([
            float(cx), float(cy),
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            color, size, life,
        ])


def update_end_animation(dt: float):
    """Оновлює позиції частинок щокадру."""
    for p in _particles:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[3] += 180 * dt   # гравiтацiя
        p[6] -= dt
    _particles[:] = [p for p in _particles if p[6] > 0]


def draw_end_animation(surface, game):
    """Малює анiмацiю перемоги та (пiсля) дiалог вибору."""
    global _end_quit_rect, _end_cont_rect

    # затемнення
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # частинки
    for p in _particles:
        pygame.draw.circle(surface, p[4],
                           (int(p[0]), int(p[1])), max(1, int(p[5])))

    # текст "ПЕРЕМОГА!"
    if game.end_anim_timer > 0:
        scale  = 1.0 + 0.04 * math.sin(pygame.time.get_ticks() / 200)
        vic    = _f("victory").render("ПЕРЕМОГА!", True, (255, 215, 0))
        w2, h2 = vic.get_size()
        vic2   = pygame.transform.scale(vic, (int(w2 * scale), int(h2 * scale)))
        surface.blit(vic2, vic2.get_rect(center=(W // 2, H // 2 - 60)))
        _txt(surface, "Ти пройшов гру!", "large", (255, 255, 200),
             W // 2, H // 2 + 30, anchor="midtop")

    # дiалог пiсля анiмацiї
    if game.show_end_dialog:
        dw, dh = min(360, W - 32), 200
        dx = (W - dw) // 2; dy = (H - dh) // 2
        bg = pygame.Surface((dw, dh), pygame.SRCALPHA)
        pygame.draw.rect(bg, (20, 15, 0, 230), (0, 0, dw, dh), border_radius=16)
        pygame.draw.rect(bg, (200, 160, 0, 255), (0, 0, dw, dh), 3, border_radius=16)
        surface.blit(bg, (dx, dy))
        _txt(surface, "Ти переміг!", "large", (255, 215, 0),
             W // 2, dy + 20, anchor="midtop")
        _txt(surface, "Що робимо далі?", "medium", (220, 220, 180),
             W // 2, dy + 58, anchor="midtop")
        bw2 = (dw - 48) // 2
        _end_quit_rect = pygame.Rect(dx + 16,           dy + 120, bw2, BTN_H)
        _end_cont_rect = pygame.Rect(dx + 16 + bw2 + 16, dy + 120, bw2, BTN_H)
        _rrect(surface, (170, 130, 0), _end_quit_rect, r=BTN_R)
        _txt(surface, "Вийти", "medbold", (40, 20, 0),
             _end_quit_rect.centerx, _end_quit_rect.centery, anchor="center")
        _rrect(surface, (40, 110, 40), _end_cont_rect, r=BTN_R)
        _txt(surface, "Грати далі", "medbold", (255, 255, 255),
             _end_cont_rect.centerx, _end_cont_rect.centery, anchor="center")


def get_end_dialog_hit(x: int, y: int):
    """Повертає 'quit' / 'continue' або None."""
    if _end_quit_rect and _end_quit_rect.collidepoint(x, y): return "quit"
    if _end_cont_rect and _end_cont_rect.collidepoint(x, y): return "continue"
    return None


# ══════════════════════════════════════════════
#  Офлайн-банер
# ══════════════════════════════════════════════
_offline_msg   = ""
_offline_timer = 0.0
_OFFLINE_DUR   = 4.0


def show_offline_message(earned: float, format_fn):
    global _offline_msg, _offline_timer
    if earned > 0:
        _offline_msg   = f"Поки вас не було: +{format_fn(earned)} монет!"
        _offline_timer = _OFFLINE_DUR


def draw_offline_message(surface, dt: float):
    global _offline_timer
    if _offline_timer <= 0:
        return
    _offline_timer -= dt
    alpha = min(255, int(255 * (_offline_timer / _OFFLINE_DUR) * 2))
    surf  = _f("medium").render(_offline_msg, True, COLOR_PASSIVE)
    surf.set_alpha(alpha)
    surface.blit(surf, surf.get_rect(
        center=(W // 2, H - TAB_BAR_H - 20)))