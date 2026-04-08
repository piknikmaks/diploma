# ─────────────────────────────────────────────
#  ui.py  —  весь рендеринг (pygame)
# ─────────────────────────────────────────────
import pygame, math, os, random, sys

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TOP_BAR_HEIGHT, GAME_AREA_WIDTH, PANEL_WIDTH, TAB_BAR_HEIGHT,
    TAB_CLICK, TAB_WORKERS, TAB_REBIRTH, TAB_ACHIEVEMENTS, TAB_STATS, TAB_SETTINGS, TABS,
    COLOR_BG, COLOR_TOP_BAR, COLOR_TOP_BAR_BORDER,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_TAB_ACTIVE, COLOR_TAB_INACTIVE, COLOR_TAB_HOVER, COLOR_TAB_BORDER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_LOCKED,
    COLOR_COIN_VAL, COLOR_PASSIVE, COLOR_CPC,
    COLOR_BTN_NORMAL, COLOR_BTN_HOVER, COLOR_BTN_LOCKED, COLOR_BTN_BORDER, COLOR_BTN_BORDER_HOV,
    COLOR_POPUP,
    COLOR_TOGGLE_ON, COLOR_TOGGLE_OFF, COLOR_TOGGLE_KNOB,
    COLOR_DELETE_BTN, COLOR_DELETE_CONFIRM, COLOR_DELETE_TEXT,
    COLOR_REBIRTH_BTN, COLOR_REBIRTH_HOVER, COLOR_REBIRTH_LOCKED, COLOR_REBIRTH_TEXT, COLOR_REBIRTH_GLOW,
    COLOR_ACH_UNLOCKED, COLOR_ACH_LOCKED, COLOR_ACH_BORDER_ON, COLOR_ACH_BORDER_OFF,
    COIN_BASE_RADIUS, COIN_GLOW_RADIUS, COIN_IMAGE_TEMPLATE,
)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# ══════════════════════════════════════════════
#  Шрифти
# ══════════════════════════════════════════════
_fonts = {}

def init_fonts():
    _fonts["huge"]        = pygame.font.SysFont("Arial", 46, bold=True)
    _fonts["large"]       = pygame.font.SysFont("Arial", 28, bold=True)
    _fonts["stat"]        = pygame.font.SysFont("Arial", 26, bold=True)
    _fonts["medium"]      = pygame.font.SysFont("Arial", 20)
    _fonts["medbold"]     = pygame.font.SysFont("Arial", 20, bold=True)
    _fonts["small"]       = pygame.font.SysFont("Arial", 16)
    _fonts["smallbold"]   = pygame.font.SysFont("Arial", 16, bold=True)
    _fonts["popup"]       = pygame.font.SysFont("Arial", 24, bold=True)
    _fonts["click_label"] = pygame.font.SysFont("Arial", 22, bold=True)
    _fonts["victory"]     = pygame.font.SysFont("Arial", 64, bold=True)

def _f(n): return _fonts[n]

# ══════════════════════════════════════════════
#  Зображення
# ══════════════════════════════════════════════
_icon_cache = {}
_coin_img   = None
_gem_imgs   = {}

def _load_image(path, size=None):
    key = (path, size)
    if key in _icon_cache: return _icon_cache[key]
    if not os.path.exists(resource_path(path)): _icon_cache[key] = None; return None
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        if size: img = pygame.transform.smoothscale(img, size)
        _icon_cache[key] = img; return img
    except: _icon_cache[key] = None; return None

def init_images():
    global _coin_img
    _coin_img = _load_image("assets/images/coin.png", (38, 38))

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

# ══════════════════════════════════════════════
#  Хелпери
# ══════════════════════════════════════════════
def _text(surface, text, font, color, x, y, anchor="topleft"):
    surf = _f(font).render(str(text), True, color)
    rect = surf.get_rect(); setattr(rect, anchor, (x, y))
    surface.blit(surf, rect); return rect

def _rrect(surface, color, rect, r=8, border=None, bw=2):
    pygame.draw.rect(surface, color, rect, border_radius=r)
    if border: pygame.draw.rect(surface, border, rect, bw, border_radius=r)

def _fmt(n):
    if n < 1_000: return str(int(n))
    elif n < 1e6:  return f"{n/1_000:.1f}K"
    elif n < 1e9:  return f"{n/1e6:.1f}M"
    elif n < 1e12: return f"{n/1e9:.1f}B"
    else:          return f"{n/1e12:.1f}T"

# ══════════════════════════════════════════════
#  Верхній бар
# ══════════════════════════════════════════════
def draw_top_bar(surface, game):
    pygame.draw.rect(surface, COLOR_TOP_BAR, (0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT))
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (0, TOP_BAR_HEIGHT-1), (WINDOW_WIDTH, TOP_BAR_HEIGHT-1), 2)
    cx = GAME_AREA_WIDTH // 2; cy = TOP_BAR_HEIGHT // 2
    coin_surf = _f("huge").render(_fmt(game.coins), True, COLOR_COIN_VAL)
    surface.blit(coin_surf, coin_surf.get_rect(midright=(cx - 4, cy)))
    if _coin_img:
        surface.blit(_coin_img, _coin_img.get_rect(midleft=(cx + 4, cy)))
    else:
        pygame.draw.circle(surface, (255,200,0), (cx+24, cy), 18)
        pygame.draw.circle(surface, (200,150,0), (cx+24, cy), 18, 3)
        _text(surface, "$", "small", (140,100,0), cx+24, cy, anchor="center")
    if game.rebirth_count > 0:
        _text(surface, f"×{int(game.rebirth_multiplier)}", "medbold",
              COLOR_REBIRTH_GLOW, GAME_AREA_WIDTH - 12, cy, anchor="midright")

# ══════════════════════════════════════════════
#  Ліва зона кліку
# ══════════════════════════════════════════════
def draw_game_area(surface, game):
    pygame.draw.rect(surface, COLOR_BG,
                     (0, TOP_BAR_HEIGHT, GAME_AREA_WIDTH, WINDOW_HEIGHT - TOP_BAR_HEIGHT))
    cx = GAME_AREA_WIDTH // 2
    cy = TOP_BAR_HEIGHT + (WINDOW_HEIGHT - TOP_BAR_HEIGHT) // 2 - 20
    _draw_gem(surface, cx, cy, game.coin_scale, game.rebirth_count)
    _text(surface, "Клік!", "click_label", COLOR_TEXT_DIM,
          cx, cy + COIN_GLOW_RADIUS + 14, anchor="midtop")
    stat_y = TOP_BAR_HEIGHT + 18
    if game.coins_per_sec > 0:
        _text(surface, f"+{_fmt(game.coins_per_sec)}/сек", "stat",
              COLOR_PASSIVE, cx, stat_y, anchor="midtop")
        stat_y += 34
    _text(surface, f"{_fmt(game.coins_per_click)} за клік", "medium",
          COLOR_CPC, cx, stat_y, anchor="midtop")
    _draw_popups(surface, game.popups)
    if game.new_achievement: _draw_achievement_banner(surface, game)

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
    for p in popups:
        surf = _f("popup").render(f"+{_fmt(p.value)}", True, COLOR_POPUP)
        surf.set_alpha(p.alpha)
        surface.blit(surf, surf.get_rect(center=(int(p.x), int(p.y))))

# ── Банер досягнення ──────────────────────────
_ach_banner_timer = 0.0
ACH_BANNER_DUR    = 3.5

def tick_achievement_banner(game, dt):
    global _ach_banner_timer
    if _ach_banner_timer > 0:
        _ach_banner_timer -= dt
        if _ach_banner_timer <= 0:
            game.new_achievement = None

def _draw_achievement_banner(surface, game):
    global _ach_banner_timer
    if game.new_achievement and _ach_banner_timer <= 0:
        _ach_banner_timer = ACH_BANNER_DUR
    if _ach_banner_timer <= 0 or not game.new_achievement: return
    ach = game.new_achievement
    bw, bh = 340, 54; bx = GAME_AREA_WIDTH//2 - bw//2; by = WINDOW_HEIGHT - bh - 50
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(s, (255,215,0,200), (0,0,bw,bh), border_radius=10)
    pygame.draw.rect(s, (200,160,0,255), (0,0,bw,bh), 2, border_radius=10)
    surface.blit(s, (bx, by))
    _text(surface, "Досягнення!", "smallbold", (100,70,0), bx+bw//2, by+6,  anchor="midtop")
    _text(surface, ach.name,         "medbold",   (60,40,0),  bx+bw//2, by+26, anchor="midtop")

# ══════════════════════════════════════════════
#  Права панель
# ══════════════════════════════════════════════
_tab_rects     = []
_upgrade_rects = []
_toggle_rects  = {}
_delete_rect   = None
_confirm_rect  = None
_confirm_mode  = False
_rebirth_rect  = None      # кнопка перерождення
_endgame_rect  = None      # кнопка кінця гри
_endgame_confirm_rects = None   # (yes_rect, no_rect)
_endgame_confirm_mode  = False
_slider_rect   = None      # трек слайдера гучності
_scroll        = {"click": 0, "worker": 0}
_SCROLL_SPEED  = 30

def draw_panel(surface, game, current_tab):
    px = GAME_AREA_WIDTH
    pygame.draw.rect(surface, COLOR_PANEL_BG, (px, 0, PANEL_WIDTH, WINDOW_HEIGHT))
    pygame.draw.line(surface, COLOR_PANEL_BORDER, (px, 0), (px, WINDOW_HEIGHT), 2)
    _draw_tab_bar(surface, px, current_tab)
    top = TOP_BAR_HEIGHT + TAB_BAR_HEIGHT
    if   current_tab == TAB_CLICK:        _draw_upgrades(surface, px, top, game, "click")
    elif current_tab == TAB_WORKERS:      _draw_upgrades(surface, px, top, game, "worker")
    elif current_tab == TAB_REBIRTH:      _draw_rebirth(surface, px, top, game)
    elif current_tab == TAB_ACHIEVEMENTS: _draw_achievements(surface, px, top, game)
    elif current_tab == TAB_STATS:        _draw_stats(surface, px, top, game)
    elif current_tab == TAB_SETTINGS:     _draw_settings(surface, px, top, game)

# ── Вкладки ───────────────────────────────────
_TAB_ICONS = {
    TAB_CLICK:        ("assets/images/icons/tab_click.png",       "⚒"),
    TAB_WORKERS:      ("assets/images/icons/tab_workers.png",      "👷"),
    TAB_REBIRTH:      ("assets/images/icons/tab_rebirth.png",      "♻"),
    TAB_ACHIEVEMENTS: ("assets/images/icons/tab_ach.png",          "🏆"),
    TAB_STATS:        ("assets/images/icons/tab_stats.png",        "📊"),
    TAB_SETTINGS:     ("assets/images/icons/tab_settings.png",     "⚙"),
}

def _draw_tab_bar(surface, px, current_tab):
    global _tab_rects
    _tab_rects.clear()
    bar_y = TOP_BAR_HEIGHT; tab_w = PANEL_WIDTH // len(TABS); pad = 6
    pygame.draw.rect(surface, COLOR_TOP_BAR, (px, bar_y, PANEL_WIDTH, TAB_BAR_HEIGHT))
    pygame.draw.line(surface, COLOR_TOP_BAR_BORDER,
                     (px, bar_y+TAB_BAR_HEIGHT-1), (px+PANEL_WIDTH, bar_y+TAB_BAR_HEIGHT-1), 2)
    mx, my = pygame.mouse.get_pos()
    for i, tab in enumerate(TABS):
        tx   = px + i*tab_w
        rect = pygame.Rect(tx+pad//2, bar_y+pad//2, tab_w-pad, TAB_BAR_HEIGHT-pad)
        _tab_rects.append(rect)
        active  = (tab == current_tab)
        hovered = rect.collidepoint(mx, my) and not active
        bg = COLOR_TAB_ACTIVE if active else (COLOR_TAB_HOVER if hovered else COLOR_TAB_INACTIVE)
        _rrect(surface, bg, rect, r=7, border=COLOR_TAB_BORDER, bw=2 if active else 1)
        path, fallback = _TAB_ICONS[tab]
        img = _load_image(path, (32, 32))
        if img:
            surface.blit(img, img.get_rect(center=rect.center))
        else:
            _text(surface, fallback, "medium", COLOR_TEXT,
                  rect.centerx, rect.centery, anchor="center")

# ── Апгрейди ─────────────────────────────────
_BTN_H = 78; _BTN_MRG = 8; _BTN_PAD = 12

def _draw_upgrades(surface, px, top_y, game, upg_type):
    global _upgrade_rects
    _upgrade_rects.clear()
    upgrades = [u for u in game.upgrades if u.type == upg_type]
    off = _scroll.get(upg_type, 0)
    mx, my = pygame.mouse.get_pos()
    clip = pygame.Rect(px, top_y, PANEL_WIDTH, WINDOW_HEIGHT-top_y)
    prev = surface.get_clip(); surface.set_clip(clip)
    for i, upg in enumerate(upgrades):
        x = px+_BTN_PAD; y = top_y+_BTN_PAD+i*(_BTN_H+_BTN_MRG)-off
        w = PANEL_WIDTH-_BTN_PAD*2
        rect = pygame.Rect(x, y, w, _BTN_H)
        if y+_BTN_H <= top_y or y >= WINDOW_HEIGHT: continue
        _upgrade_rects.append((rect, upg.id))
        can = game.coins >= upg.current_cost
        hov = rect.collidepoint(mx, my)
        bg  = (COLOR_BTN_HOVER if hov else COLOR_BTN_NORMAL) if can else COLOR_BTN_LOCKED
        brd = (COLOR_BTN_BORDER_HOV if hov else COLOR_BTN_BORDER) if can else COLOR_BTN_BORDER
        _rrect(surface, bg, rect, r=8, border=brd, bw=2)
        isz = 54; ir = pygame.Rect(x+10, y+(_BTN_H-isz)//2, isz, isz)
        img = _load_image(upg.icon_path, (isz,isz)) if upg.icon_path else None
        if img: surface.blit(img, ir)
        else:
            _rrect(surface, (170,170,190), ir, r=6, border=COLOR_BTN_BORDER, bw=1)
            _text(surface, upg.name[0].upper(), "medbold", COLOR_TEXT_DIM,
                  ir.centerx, ir.centery, anchor="center")
        tx = ir.right+10; ty = y+12
        _text(surface, upg.name, "medbold", COLOR_TEXT if can else COLOR_TEXT_LOCKED, tx, ty)
        _text(surface, upg.description, "small", COLOR_TEXT_DIM, tx, ty+22)
        cc = (180,130,0) if can else (160,100,100)
        cs = _fmt(upg.current_cost)
        if _coin_img:
            ci = pygame.transform.smoothscale(_coin_img, (20,20))
            surface.blit(ci, (tx, ty+44))
            _text(surface, cs, "small", cc, tx+24, ty+44)
        else:
            _text(surface, f"$ {cs}", "small", cc, tx, ty+44)
        if upg.level > 0:
            _text(surface, f"Рвн.{upg.level}", "small", COLOR_PASSIVE,
                  rect.right-10, y+10, anchor="topright")
    surface.set_clip(prev)
    total_h = len(upgrades)*(_BTN_H+_BTN_MRG)+_BTN_PAD
    vis = WINDOW_HEIGHT-top_y
    if total_h > vis:
        bw=6; bx=px+PANEL_WIDTH-bw-4
        ratio=vis/total_h; th=max(30,int(vis*ratio))
        max_off=max(1, total_h-vis)
        ty2=top_y+int((min(off,max_off)/max_off)*(vis-th))
        pygame.draw.rect(surface,(180,180,180),(bx,top_y,bw,vis),border_radius=3)
        pygame.draw.rect(surface,(110,110,130),(bx,ty2,bw,th),border_radius=3)

# ── Перерождення ─────────────────────────────
def _draw_rebirth(surface, px, top_y, game):
    global _rebirth_rect, _endgame_rect, _endgame_confirm_rects
    _rebirth_rect = _endgame_rect = _endgame_confirm_rects = None
    cx = px + PANEL_WIDTH//2
    y  = top_y + 20

    _text(surface, "Перерождення", "large", COLOR_TEXT, cx, y, anchor="midtop"); y += 46
    _text(surface, f"Кількість: {game.rebirth_count}", "medbold",
          COLOR_PASSIVE, cx, y, anchor="midtop"); y += 30
    mult = f"Множник доходу: ×{int(game.rebirth_multiplier)}"
    _text(surface, mult, "medium", COLOR_TEXT_DIM, cx, y, anchor="midtop"); y += 32
    pygame.draw.line(surface, COLOR_PANEL_BORDER, (px+20, y), (px+PANEL_WIDTH-20, y), 1); y += 14

    _text(surface, "Наступне перерождення:", "medium",
          COLOR_TEXT_DIM, cx, y, anchor="midtop"); y += 28
    can = game.can_rebirth()
    cost_col = (180,130,0) if can else (160,100,100)
    _text(surface, f"Ціна: {_fmt(game.rebirth_cost)} монет", "medbold",
          cost_col, cx, y, anchor="midtop"); y += 26
    _text(surface, f"Дасть множник ×{int(game.rebirth_multiplier)*2}", "medium",
          COLOR_TEXT_DIM, cx, y, anchor="midtop"); y += 26
    _text(surface, "Монети і апгрейди скинуться!", "small",
          (180,100,0), cx, y, anchor="midtop"); y += 36

    # кнопка перерождення
    bw = PANEL_WIDTH-48; bh = 50; bx = px+24
    _rebirth_rect = pygame.Rect(bx, y, bw, bh)
    mx, my = pygame.mouse.get_pos()
    hov = _rebirth_rect.collidepoint(mx, my)
    bg  = (COLOR_REBIRTH_HOVER if hov else COLOR_REBIRTH_BTN) if can else COLOR_REBIRTH_LOCKED
    _rrect(surface, bg, _rebirth_rect, r=10)
    _text(surface, "Переродитися", "large",
          COLOR_REBIRTH_TEXT if can else COLOR_TEXT_LOCKED,
          _rebirth_rect.centerx, _rebirth_rect.centery, anchor="center")
    y += bh + 14

    # прогрес-бар
    progress = min(1.0, game.coins / max(1, game.rebirth_cost))
    ph = 14; py2 = y
    pygame.draw.rect(surface, (200,200,200), (bx, py2, bw, ph), border_radius=7)
    if progress > 0:
        pygame.draw.rect(surface, COLOR_REBIRTH_BTN,
                         (bx, py2, int(bw*progress), ph), border_radius=7)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bx, py2, bw, ph), 2, border_radius=7)
    _text(surface, f"{progress*100:.1f}%", "small", COLOR_TEXT_DIM,
          bx+bw//2, py2+ph+4, anchor="midtop")
    y += ph + 28

    # ── Кнопка кінця гри (тільки якщо всі досягнення) ──
    if game.all_achievements_unlocked:
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (px+20, y), (px+PANEL_WIDTH-20, y), 1)
        y += 12
        _text(surface, "Всі досягнення виконано!", "smallbold",
              (140,100,0), cx, y, anchor="midtop"); y += 26
        eg_can = game.can_end_game()
        eg_cost_col = (180,130,0) if eg_can else (160,100,100)
        _text(surface, f"Ціна фіналу: {_fmt(game.end_game_cost)}", "medium",
              eg_cost_col, cx, y, anchor="midtop"); y += 30

        if _endgame_confirm_mode:
            # підтвердження
            _text(surface, "Ви впевнені? Це завершить гру!", "smallbold",
                  (100,50,0), cx, y, anchor="midtop"); y += 28
            hw = (bw-12)//2
            yes = pygame.Rect(bx,       y, hw, 44)
            no  = pygame.Rect(bx+hw+12, y, hw, 44)
            _rrect(surface, (200,160,0), yes, r=8)
            _text(surface, "Завершити!", "medbold", (60,30,0),
                  yes.centerx, yes.centery, anchor="center")
            _rrect(surface, (150,150,150), no, r=8)
            _text(surface, "Скасувати", "medbold", (255,255,255),
                  no.centerx, no.centery, anchor="center")
            _endgame_confirm_rects = (yes, no)
        else:
            _endgame_rect = pygame.Rect(bx, y, bw, 50)
            hov2 = _endgame_rect.collidepoint(mx, my)
            if eg_can:
                bg2 = (240,190,0) if hov2 else (220,170,0)
            else:
                bg2 = (190,190,190)
            _rrect(surface, bg2, _endgame_rect, r=10)
            _text(surface, "Завершити гру", "large",
                  (60,30,0) if eg_can else COLOR_TEXT_LOCKED,
                  _endgame_rect.centerx, _endgame_rect.centery, anchor="center")

# ── Досягнення ────────────────────────────────
_ACH_W=64; _ACH_H=64; _ACH_PAD=10; _ACH_COLS=5

def _draw_achievements(surface, px, top_y, game):
    cx = px+PANEL_WIDTH//2
    _text(surface, "Досягнення", "large", COLOR_TEXT, cx, top_y+14, anchor="midtop")
    unlocked = sum(1 for a in game.achievements if a.unlocked)
    _text(surface, f"{unlocked} / {len(game.achievements)}", "medium",
          COLOR_TEXT_DIM, cx, top_y+46, anchor="midtop")
    sx = px+(PANEL_WIDTH-(_ACH_COLS*(_ACH_W+_ACH_PAD)-_ACH_PAD))//2
    mx, my = pygame.mouse.get_pos(); tooltip = None
    for i, ach in enumerate(game.achievements):
        col = i%_ACH_COLS; row = i//_ACH_COLS
        x = sx+col*(_ACH_W+_ACH_PAD); y = top_y+80+row*(_ACH_H+_ACH_PAD+4)
        rect = pygame.Rect(x, y, _ACH_W, _ACH_H)
        bg = COLOR_ACH_UNLOCKED if ach.unlocked else COLOR_ACH_LOCKED
        brd = COLOR_ACH_BORDER_ON if ach.unlocked else COLOR_ACH_BORDER_OFF
        _rrect(surface, bg, rect, r=8, border=brd, bw=2 if ach.unlocked else 1)
        img = _load_image(ach.icon, (_ACH_W-16, _ACH_H-16)) if ach.icon else None
        if img:
            ir = img.get_rect(center=rect.center)
            if not ach.unlocked:
                dark = img.copy()
                dark.fill((0,0,0,140), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(dark, ir)
            else:
                surface.blit(img, ir)
        else:
            sym = "🏆" if ach.unlocked else "🔒"
            _text(surface, sym, "medbold",
                  (100,70,0) if ach.unlocked else COLOR_TEXT_LOCKED,
                  rect.centerx, rect.centery, anchor="center")
        if rect.collidepoint(mx, my): tooltip = (ach, rect)
    if tooltip:
        ach, rect = tooltip
        tw, th = 240, 72
        tx = min(rect.right+8, px+PANEL_WIDTH-tw-8)
        ty = max(top_y+4, rect.top-th//2)
        bg2 = pygame.Surface((tw,th), pygame.SRCALPHA)
        pygame.draw.rect(bg2, (40,40,40,220), (0,0,tw,th), border_radius=8)
        surface.blit(bg2, (tx,ty))
        pygame.draw.rect(surface, (80,80,80), (tx,ty,tw,th), 1, border_radius=8)
        nc = (255,215,0) if ach.unlocked else (200,200,200)
        _text(surface, ach.name, "medbold", nc, tx+10, ty+10)
        _text(surface, ach.desc, "small", (200,200,200), tx+10, ty+32)
        sc = (100,220,100) if ach.unlocked else (160,100,100)
        _text(surface, "Отримано" if ach.unlocked else "Заблоковано",
              "small", sc, tx+10, ty+52)

# ── Статистика ────────────────────────────────
def _draw_stats(surface, px, top_y, game):
    cx = px+PANEL_WIDTH//2
    _text(surface, "Статистика", "large", COLOR_TEXT, cx, top_y+14, anchor="midtop")
    rows = [
        ("Монет зараз",        _fmt(game.coins)),
        ("Всього зароблено",    _fmt(game.total_earned)),
        ("Монет за клік",       _fmt(game.coins_per_click)),
        ("Монет за секунду",    _fmt(game.coins_per_sec)),
        ("Кліків зроблено",     f"{game.total_clicks:,}"),
        ("Переороджень",        str(game.rebirth_count)),
        ("Множник доходу",      f"×{int(game.rebirth_multiplier)}"),
        ("Час у грі",           game.format_time(game.total_play_time)),
        ("Досягнень відкрито",  f"{sum(1 for a in game.achievements if a.unlocked)} / {len(game.achievements)}"),
    ]
    y = top_y+60
    for label, val in rows:
        _text(surface, label+":", "small", COLOR_TEXT_DIM, px+24, y)
        _text(surface, val, "medbold", COLOR_TEXT, px+PANEL_WIDTH-24, y, anchor="topright")
        y += 28
        pygame.draw.line(surface, COLOR_PANEL_BORDER,
                         (px+18, y-2), (px+PANEL_WIDTH-18, y-2), 1)

# ── Налаштування ──────────────────────────────
_TOGGLE_W=80; _TOGGLE_H=36
_SLD_H=16   # висота треку слайдера

def _draw_settings(surface, px, top_y, game):
    global _toggle_rects, _delete_rect, _confirm_rect, _slider_rect
    _toggle_rects.clear()
    _delete_rect = _confirm_rect = _slider_rect = None

    cx = px+PANEL_WIDTH//2
    _text(surface, "Налаштування", "large", COLOR_TEXT, cx, top_y+24, anchor="midtop")
    y = top_y + 80

    # ── Звуки монети (тогл) ──
    _text(surface, "Звуки монети:", "medium", COLOR_TEXT,
          cx - _TOGGLE_W//2 - 10, y+4, anchor="midright")
    tog_r = pygame.Rect(cx-_TOGGLE_W//2, y, _TOGGLE_W, _TOGGLE_H)
    _toggle_rects["sound"] = tog_r
    _draw_toggle(surface, tog_r, game.sound_on)
    y += 64

    # ── Гучність музики (слайдер) ──
    _text(surface, "Гучність музики:", "medium", COLOR_TEXT, px+24, y)
    y += 28
    sw = PANEL_WIDTH-48; sx = px+24
    _slider_rect = pygame.Rect(sx, y, sw, _SLD_H)
    _draw_volume_slider(surface, _slider_rect, game.music_volume)
    vol_pct = f"{int(game.music_volume*100)}%"
    _text(surface, vol_pct, "medbold", COLOR_TEXT, cx, y+_SLD_H+6, anchor="midtop")
    y += _SLD_H + 36

    # ── Кнопка видалення ──
    _delete_rect = pygame.Rect(px+24, y, PANEL_WIDTH-48, 44)
    if _confirm_mode:
        _rrect(surface, (240,240,240), _delete_rect, r=8, border=(180,180,180), bw=2)
        _text(surface, "Ви впевнені?", "medbold", (80,80,80),
              _delete_rect.centerx, _delete_rect.centery-10, anchor="center")
        hw = (PANEL_WIDTH-60)//2
        yes = pygame.Rect(px+24,        y+44+8, hw, 40)
        no  = pygame.Rect(px+24+hw+12,  y+44+8, hw, 40)
        _rrect(surface, COLOR_DELETE_CONFIRM, yes, r=8)
        _text(surface, "Видалити", "medbold", COLOR_DELETE_TEXT,
              yes.centerx, yes.centery, anchor="center")
        _rrect(surface, (160,160,160), no, r=8)
        _text(surface, "Скасувати", "medbold", COLOR_DELETE_TEXT,
              no.centerx, no.centery, anchor="center")
        _confirm_rect = (yes, no)
    else:
        mx, my = pygame.mouse.get_pos()
        hov = _delete_rect.collidepoint(mx, my)
        _rrect(surface, COLOR_DELETE_CONFIRM if hov else COLOR_DELETE_BTN, _delete_rect, r=8)
        _text(surface, "Видалити прогрес", "medbold", COLOR_DELETE_TEXT,
              _delete_rect.centerx, _delete_rect.centery, anchor="center")

    _text(surface, "S — зберегти гру", "small", COLOR_TEXT_DIM,
          cx, WINDOW_HEIGHT-30, anchor="midbottom")

def _draw_toggle(surface, rect, state):
    bg = COLOR_TOGGLE_ON if state else COLOR_TOGGLE_OFF
    pygame.draw.rect(surface, bg, rect, border_radius=_TOGGLE_H//2)
    m = 3; kr = _TOGGLE_H//2-m
    kx = rect.right-kr-m if state else rect.left+kr+m
    pygame.draw.circle(surface, COLOR_TOGGLE_KNOB, (kx, rect.centery), kr)
    lbl = "ON" if state else "OFF"
    lx  = rect.left+8 if state else rect.right-8
    anc = "midleft" if state else "midright"
    _text(surface, lbl, "small", (255,255,255) if state else (120,120,120),
          lx, rect.centery, anchor=anc)

def _draw_volume_slider(surface, rect, volume):
    """Малює слайдер гучності. volume: 0.0–1.0"""
    # трек
    pygame.draw.rect(surface, (190,190,190), rect, border_radius=_SLD_H//2)
    # заповнена частина
    if volume > 0:
        fill = pygame.Rect(rect.x, rect.y, int(rect.w*volume), rect.h)
        pygame.draw.rect(surface, COLOR_TOGGLE_ON, fill, border_radius=_SLD_H//2)
    pygame.draw.rect(surface, (150,150,150), rect, 2, border_radius=_SLD_H//2)
    # ручка
    knob_x = rect.x + int(rect.w * volume)
    knob_x = max(rect.x + 10, min(rect.right - 10, knob_x))
    pygame.draw.circle(surface, (255,255,255), (knob_x, rect.centery), 11)
    pygame.draw.circle(surface, (120,120,120), (knob_x, rect.centery), 11, 2)

# ── Кінцева анімація ──────────────────────────
_particles = []   # list of [x, y, vx, vy, color, size, life]

def start_end_animation():
    """Створює частинки феєрверку в центрі лівої зони."""
    global _particles
    cx = GAME_AREA_WIDTH // 2
    cy = WINDOW_HEIGHT   // 2
    _particles.clear()
    for _ in range(200):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 400)
        color = random.choice([
            (255,215,0),(255,180,0),(255,100,0),(255,255,100),
            (200,255,100),(100,220,255),(220,100,255),(255,80,80),
        ])
        size  = random.randint(4, 10)
        life  = random.uniform(1.5, 3.5)
        _particles.append([
            float(cx), float(cy),
            math.cos(angle)*speed, math.sin(angle)*speed,
            color, size, life
        ])

def update_end_animation(dt):
    for p in _particles:
        p[0] += p[2]*dt; p[1] += p[3]*dt
        p[3] += 200*dt   # гравітація
        p[6] -= dt
    _particles[:] = [p for p in _particles if p[6] > 0]

def draw_end_animation(surface, game):
    """Малює анімацію і (після неї) діалог вибору."""
    # затемнення
    overlay = pygame.Surface((GAME_AREA_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # частинки
    for p in _particles:
        alpha = min(255, int(255 * p[6] / 2.0))
        r, g, b = p[4]
        pygame.draw.circle(surface, (r,g,b), (int(p[0]), int(p[1])), max(1, int(p[5])))

    # текст ПЕРЕМОГА
    if game.end_anim_timer > 0:
        cx = GAME_AREA_WIDTH // 2; cy = WINDOW_HEIGHT // 2
        surf = _f("victory").render("ПЕРЕМОГА!", True, (255, 215, 0))
        # пульсація
        scale = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
        w, h  = surf.get_size()
        surf2 = pygame.transform.scale(surf, (int(w*scale), int(h*scale)))
        surface.blit(surf2, surf2.get_rect(center=(cx, cy-40)))
        _text(surface, "Ти пройшов гру!", "large", (255,255,200),
              cx, cy+50, anchor="midtop")

    # діалог після анімації
    if game.show_end_dialog:
        _draw_end_dialog(surface, game)

def _draw_end_dialog(surface, game):
    cx = GAME_AREA_WIDTH // 2; cy = WINDOW_HEIGHT // 2
    dw, dh = 420, 240
    dx = cx - dw//2; dy = cy - dh//2
    bg = pygame.Surface((dw, dh), pygame.SRCALPHA)
    pygame.draw.rect(bg, (20, 15, 0, 230), (0, 0, dw, dh), border_radius=16)
    pygame.draw.rect(bg, (200,160,0,255),  (0, 0, dw, dh), 3, border_radius=16)
    surface.blit(bg, (dx, dy))
    _text(surface, "🏆 Ти переміг!", "large", (255,215,0), cx, dy+24, anchor="midtop")
    _text(surface, "Що робимо далі?", "medium", (220,220,180), cx, dy+68, anchor="midtop")
    # кнопки
    bw2 = (dw-48)//2
    quit_rect = pygame.Rect(dx+16,       dy+130, bw2, 52)
    cont_rect = pygame.Rect(dx+16+bw2+16, dy+130, bw2, 52)
    mx, my = pygame.mouse.get_pos()
    _rrect(surface, (200,160,0) if quit_rect.collidepoint(mx,my) else (170,130,0), quit_rect, r=10)
    _text(surface, "Вийти", "medbold", (40,20,0), quit_rect.centerx, quit_rect.centery, anchor="center")
    _rrect(surface, (60,140,60) if cont_rect.collidepoint(mx,my) else (40,110,40), cont_rect, r=10)
    _text(surface, "Грати далі", "medbold", (255,255,255), cont_rect.centerx, cont_rect.centery, anchor="center")
    # зберігаємо ректи для hit-test
    global _end_dialog_quit, _end_dialog_cont
    _end_dialog_quit = quit_rect
    _end_dialog_cont = cont_rect

_end_dialog_quit = None
_end_dialog_cont = None

# ══════════════════════════════════════════════
#  Публічні hit-test
# ══════════════════════════════════════════════
def get_clicked_tab(mx, my):
    for i, r in enumerate(_tab_rects):
        if r.collidepoint(mx, my): return TABS[i]
    return None

def get_clicked_upgrade(mx, my):
    for r, uid in _upgrade_rects:
        if r.collidepoint(mx, my): return uid
    return None

def get_clicked_toggle(mx, my):
    for k, r in _toggle_rects.items():
        if r.collidepoint(mx, my): return k
    return None

def get_clicked_delete(mx, my):
    if _confirm_mode and _confirm_rect:
        y_r, n_r = _confirm_rect
        if y_r.collidepoint(mx, my): return "yes"
        if n_r.collidepoint(mx, my): return "no"
        return None
    if _delete_rect and _delete_rect.collidepoint(mx, my): return "delete"
    return None

def get_clicked_rebirth(mx, my):
    return bool(_rebirth_rect and _rebirth_rect.collidepoint(mx, my))

def get_clicked_endgame(mx, my):
    """Повертає 'endgame'/'yes'/'no'/None"""
    global _endgame_confirm_mode
    if _endgame_confirm_mode and _endgame_confirm_rects:
        y_r, n_r = _endgame_confirm_rects
        if y_r.collidepoint(mx, my): return "yes"
        if n_r.collidepoint(mx, my): return "no"
        return None
    if _endgame_rect and _endgame_rect.collidepoint(mx, my): return "endgame"
    return None

def get_clicked_end_dialog(mx, my):
    """Повертає 'quit'/'continue'/None"""
    if _end_dialog_quit and _end_dialog_quit.collidepoint(mx, my): return "quit"
    if _end_dialog_cont and _end_dialog_cont.collidepoint(mx, my): return "continue"
    return None

def slider_volume_at(mx):
    """Повертає гучність (0.0–1.0) за x-координатою кліку на слайдері."""
    if _slider_rect is None: return None
    val = (mx - _slider_rect.x) / max(1, _slider_rect.w)
    return max(0.0, min(1.0, val))

def is_on_slider(mx, my):
    if _slider_rect is None: return False
    expanded = _slider_rect.inflate(0, 20)   # трохи ширша зона
    return expanded.collidepoint(mx, my)

def set_confirm_mode(val): global _confirm_mode;           _confirm_mode = val
def set_endgame_confirm(val): global _endgame_confirm_mode; _endgame_confirm_mode = val

def scroll_upgrades(tab, delta):
    if tab in _scroll: _scroll[tab] = max(0, _scroll[tab] + delta * _SCROLL_SPEED)

def get_coin_center():
    return GAME_AREA_WIDTH//2, TOP_BAR_HEIGHT+(WINDOW_HEIGHT-TOP_BAR_HEIGHT)//2-20

# ══════════════════════════════════════════════
#  Офлайн-банер
# ══════════════════════════════════════════════
_offline_msg=""; _offline_timer=0.0; OFFLINE_MSG_DUR=4.0

def show_offline_message(earned, format_fn):
    global _offline_msg, _offline_timer
    if earned > 0:
        _offline_msg   = f"Поки вас не було: +{format_fn(earned)} монет!"
        _offline_timer = OFFLINE_MSG_DUR

def draw_offline_message(surface, dt):
    global _offline_timer
    if _offline_timer <= 0: return
    _offline_timer -= dt
    alpha = min(255, int(255*(_offline_timer/OFFLINE_MSG_DUR)*2))
    surf  = _f("medium").render(_offline_msg, True, COLOR_PASSIVE)
    surf.set_alpha(alpha)
    surface.blit(surf, surf.get_rect(center=(GAME_AREA_WIDTH//2, WINDOW_HEIGHT-36)))