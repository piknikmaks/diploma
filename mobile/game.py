# ─────────────────────────────────────────────
#  game.py  —  ігровий стан і вся логіка
# ─────────────────────────────────────────────
import time
import math
from settings_mobile import (
    UPGRADES, ACHIEVEMENTS,
    OFFLINE_INCOME_CAP, POPUP_LIFETIME, POPUP_SPEED,
    MAX_CLICKS_PER_SEC, REBIRTH_BASE_COST,
    COIN_CLICK_SCALE, COIN_ANIM_SPEED,
)


# ══════════════════════════════════════════════
class PopupNumber:
    def __init__(self, x, y, value):
        self.x = x; self.y = y; self.value = value; self.elapsed = 0.0

    @property
    def alive(self):  return self.elapsed < POPUP_LIFETIME
    @property
    def alpha(self):  return max(0, int(255 * (1.0 - self.elapsed / POPUP_LIFETIME)))
    def update(self, dt): self.elapsed += dt; self.y -= POPUP_SPEED * dt


# ══════════════════════════════════════════════
class Upgrade:
    def __init__(self, template, level=0):
        self.id          = template["id"]
        self.name        = template["name"]
        self.description = template["description"]
        self.base_cost   = template["base_cost"]
        self.cost_mult   = template["cost_mult"]
        self.click_bonus = template["click_bonus"]
        self.passive     = template["passive"]
        self.icon_path   = template["icon"]
        self.type        = template.get("type", "click")
        self.level       = level

    @property
    def current_cost(self):
        return math.ceil(self.base_cost * (self.cost_mult ** self.level))

    def to_dict(self):
        return {"id": self.id, "level": self.level}


# ══════════════════════════════════════════════
class Achievement:
    def __init__(self, template, unlocked=False):
        self.id              = template["id"]
        self.name            = template["name"]
        self.desc            = template["desc"]
        self.icon            = template.get("icon")
        self.condition_type  = template["condition_type"]
        self.condition_value = template["condition_value"]
        self.unlocked        = unlocked
        self.unlock_time     = None

    def check(self, gs):
        if self.unlocked: return False
        ct, cv = self.condition_type, self.condition_value
        if ct == "total_earned":  return gs.total_earned  >= cv
        if ct == "total_clicks":  return gs.total_clicks  >= cv
        if ct == "rebirths":      return gs.rebirth_count >= cv
        if ct == "upgrade_level":
            upg = gs._get_upgrade(cv["upgrade_id"])
            return upg is not None and upg.level >= cv["level"]
        return False


# ══════════════════════════════════════════════
class GameState:
    def __init__(self):
        # ── Ресурси ──────────────────────────────
        self.coins:        float = 0.0
        self.total_earned: float = 0.0

        # ── Апгрейди ─────────────────────────────
        self.upgrades = [Upgrade(t) for t in UPGRADES]

        # ── Кеш статів ───────────────────────────
        self.coins_per_click: float = 1.0
        self.coins_per_sec:   float = 0.0

        # ── Перерождення ─────────────────────────
        self.rebirth_count:      int   = 0
        self.rebirth_multiplier: float = 1.0

        # ── Кінець гри ───────────────────────────
        self.game_completed:   bool  = False   # анімація вже показана
        self.end_anim_timer:   float = 0.0     # > 0 поки йде анімація
        self.show_end_dialog:  bool  = False   # чи показувати вибір

        # ── Статистика ───────────────────────────
        self.total_clicks:    int   = 0
        self.total_play_time: float = 0.0

        # ── Досягнення ───────────────────────────
        self.achievements = [Achievement(t) for t in ACHIEVEMENTS]
        self.new_achievement = None

        # ── Спливаючі числа ──────────────────────
        self.popups = []

        # ── Анімація монети ──────────────────────
        self.coin_scale: float = 1.0

        # ── Ліміт кліків ─────────────────────────
        self._click_tokens: float = MAX_CLICKS_PER_SEC

        # ── Налаштування ─────────────────────────
        self.sound_on:     bool  = True
        self.music_volume: float = 0.3   # 0.0 – 1.0 (замінює music_on)

        self._ach_timer: float = 0.0
        self.last_save_time: float = time.time()

    # ─────────────────────────────────────────
    def _recalc_stats(self):
        cpc = 1.0; cps = 0.0
        for upg in self.upgrades:
            cpc += upg.click_bonus * upg.level
            cps += upg.passive     * upg.level
        self.coins_per_click = cpc * self.rebirth_multiplier
        self.coins_per_sec   = cps * self.rebirth_multiplier

    # ─────────────────────────────────────────
    def on_click(self, x, y):
        if self._click_tokens < 1.0: return False
        self._click_tokens -= 1.0
        earned = self.coins_per_click
        self.coins += earned; self.total_earned += earned
        self.total_clicks += 1
        self.coin_scale = COIN_CLICK_SCALE
        self.popups.append(PopupNumber(x, y, earned))
        return True

    # ─────────────────────────────────────────
    def buy_upgrade(self, uid):
        upg = self._get_upgrade(uid)
        if upg is None or self.coins < upg.current_cost: return False
        self.coins -= upg.current_cost
        upg.level  += 1
        self._recalc_stats()
        return True

    # ─────────────────────────────────────────
    @property
    def rebirth_cost(self):
        return REBIRTH_BASE_COST * (4 ** self.rebirth_count)

    def can_rebirth(self):
        return self.coins >= self.rebirth_cost

    def do_rebirth(self):
        if not self.can_rebirth(): return False
        self.rebirth_count     += 1
        self.rebirth_multiplier = float(2 ** self.rebirth_count)
        self.coins = 0.0
        for upg in self.upgrades: upg.level = 0
        self._recalc_stats()
        return True

    # ─────────────────────────────────────────
    #  Кінець гри
    # ─────────────────────────────────────────
    @property
    def all_achievements_unlocked(self):
        return all(a.unlocked for a in self.achievements)

    @property
    def end_game_cost(self):
        return self.rebirth_cost * 5

    def can_end_game(self):
        return self.all_achievements_unlocked and self.coins >= self.end_game_cost

    def do_end_game(self):
        if not self.can_end_game(): return False
        self.coins     -= self.end_game_cost
        self.end_anim_timer  = 5.0   # 5 секунд анімації
        self.game_completed  = True
        return True

    # ─────────────────────────────────────────
    def _check_achievements(self):
        for ach in self.achievements:
            if ach.check(self):
                ach.unlocked    = True
                ach.unlock_time = time.time()
                self.new_achievement = ach

    # ─────────────────────────────────────────
    def update(self, dt):
        self._click_tokens = min(
            self._click_tokens + MAX_CLICKS_PER_SEC * dt, MAX_CLICKS_PER_SEC)

        if self.coins_per_sec > 0:
            earned = self.coins_per_sec * dt
            self.coins += earned; self.total_earned += earned

        if self.coin_scale > 1.0:
            self.coin_scale -= COIN_ANIM_SPEED
            if self.coin_scale < 1.0: self.coin_scale = 1.0

        for p in self.popups: p.update(dt)
        self.popups = [p for p in self.popups if p.alive]

        self._ach_timer += dt
        if self._ach_timer >= 0.16:
            self._check_achievements(); self._ach_timer = 0.0

        self.total_play_time += dt

        # відлік анімації кінця
        if self.end_anim_timer > 0:
            self.end_anim_timer -= dt
            if self.end_anim_timer <= 0:
                self.end_anim_timer = 0.0
                self.show_end_dialog = True

    # ─────────────────────────────────────────
    def apply_offline_income(self, seconds_away):
        seconds_away = min(seconds_away, OFFLINE_INCOME_CAP)
        if self.coins_per_sec <= 0 or seconds_away <= 0: return 0.0
        earned = self.coins_per_sec * seconds_away
        self.coins += earned; self.total_earned += earned
        return earned

    # ─────────────────────────────────────────
    def to_dict(self):
        return {
            "coins":           self.coins,
            "total_earned":    self.total_earned,
            "timestamp":       time.time(),
            "upgrades":        [u.to_dict() for u in self.upgrades],
            "sound_on":        self.sound_on,
            "music_volume":    self.music_volume,
            "rebirth_count":   self.rebirth_count,
            "total_clicks":    self.total_clicks,
            "total_play_time": self.total_play_time,
            "game_completed":  self.game_completed,
            "achievements":    [
                {"id": a.id, "unlocked": a.unlocked, "unlock_time": a.unlock_time}
                for a in self.achievements
            ],
        }

    def from_dict(self, data):
        self.coins           = float(data.get("coins", 0))
        self.total_earned    = float(data.get("total_earned", 0))
        self.sound_on        = bool(data.get("sound_on", True))
        self.music_volume    = float(data.get("music_volume",
                                     0.3 if data.get("music_on", True) else 0.0))
        self.total_clicks    = int(data.get("total_clicks", 0))
        self.total_play_time = float(data.get("total_play_time", 0))
        self.game_completed  = bool(data.get("game_completed", False))

        self.rebirth_count      = int(data.get("rebirth_count", 0))
        self.rebirth_multiplier = float(2 ** self.rebirth_count)

        saved_levels = {u["id"]: u["level"] for u in data.get("upgrades", [])}
        for upg in self.upgrades:
            upg.level = saved_levels.get(upg.id, 0)

        saved_ach = {a["id"]: a for a in data.get("achievements", [])}
        for ach in self.achievements:
            sd = saved_ach.get(ach.id, {})
            ach.unlocked    = bool(sd.get("unlocked", False))
            ach.unlock_time = sd.get("unlock_time")

        self._recalc_stats()

        saved_time = data.get("timestamp")
        if saved_time:
            return self.apply_offline_income(time.time() - float(saved_time))
        return 0.0

    # ─────────────────────────────────────────
    def _get_upgrade(self, uid):
        for upg in self.upgrades:
            if upg.id == uid: return upg
        return None

    @staticmethod
    def format_number(n):
        if n < 1_000:    return str(int(n))
        elif n < 1e6:    return f"{n/1_000:.1f}K"
        elif n < 1e9:    return f"{n/1e6:.1f}M"
        elif n < 1e12:   return f"{n/1e9:.1f}B"
        else:            return f"{n/1e12:.1f}T"

    @staticmethod
    def format_time(s):
        s = int(s)
        h = s // 3600; s -= h * 3600
        m = s // 60;   s -= m * 60
        if h: return f"{h}г {m:02d}хв {s:02d}с"
        if m: return f"{m}хв {s:02d}с"
        return f"{s}с"