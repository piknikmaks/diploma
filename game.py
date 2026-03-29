# ─────────────────────────────────────────────
#  game.py  —  ігровий стан і вся логіка
# ─────────────────────────────────────────────
import time
import math
from settings import UPGRADES, OFFLINE_INCOME_CAP, POPUP_LIFETIME, POPUP_SPEED, MAX_CLICKS_PER_SEC


# ══════════════════════════════════════════════
#  Клас спливаючого числа (+N над монетою)
# ══════════════════════════════════════════════
class PopupNumber:
    """Анімований текст, що з'являється при кліку і повільно зникає вгору."""

    def __init__(self, x: float, y: float, value: float):
        self.x       = x
        self.y       = y
        self.value   = value
        self.elapsed = 0.0          # скільки секунд існує

    @property
    def alive(self) -> bool:
        return self.elapsed < POPUP_LIFETIME

    @property
    def alpha(self) -> int:
        """Прозорість 255→0 по мірі зникання."""
        ratio = 1.0 - (self.elapsed / POPUP_LIFETIME)
        return max(0, int(255 * ratio))

    def update(self, dt: float):
        self.elapsed += dt
        self.y       -= POPUP_SPEED * dt   # рухається вгору


# ══════════════════════════════════════════════
#  Клас одного апгрейду (runtime-стан)
# ══════════════════════════════════════════════
class Upgrade:
    """
    Зберігає поточний рівень і обчислює актуальну ціну.
    Дані шаблону беруться з settings.UPGRADES.
    """

    def __init__(self, template: dict, level: int = 0):
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
    def current_cost(self) -> float:
        """Ціна наступного рівня: base_cost * mult^level (округлена)."""
        return math.ceil(self.base_cost * (self.cost_mult ** self.level))

    def to_dict(self) -> dict:
        return {"id": self.id, "level": self.level}


# ══════════════════════════════════════════════
#  Головний клас стану гри
# ══════════════════════════════════════════════
class GameState:
    """
    Містить весь ігровий стан:
      - монети та їх джерела
      - список апгрейдів
      - спливаючі числа
      - анімацію монети
    Не знає нічого про pygame і не малює нічого сам.
    """

    def __init__(self):
        # ── Ресурси ──────────────────────────────
        self.coins: float = 0.0          # поточна кількість монет
        self.total_earned: float = 0.0   # всього зароблено за всю гру

        # ── Апгрейди ─────────────────────────────
        self.upgrades: list[Upgrade] = [
            Upgrade(tmpl) for tmpl in UPGRADES
        ]

        # ── Кеш статів (перераховується після кожної покупки) ──
        self.coins_per_click: float = 1.0   # монет за один клік
        self.coins_per_sec:   float = 0.0   # пасивний дохід

        # ── Спливаючі числа ──────────────────────
        self.popups: list[PopupNumber] = []

        # ── Анімація монети ──────────────────────
        self.coin_scale: float = 1.0        # поточний масштаб (1.0 = норма)

        # ── Ліміт кліків ──────────────────────────
        self._click_tokens: float = MAX_CLICKS_PER_SEC  # поточні доступні кліки

        # ── Налаштування ─────────────────────────
        self.sound_on: bool = True
        self.music_on: bool = True

        # ── Час ──────────────────────────────────
        self.last_save_time: float = time.time()

    # ─────────────────────────────────────────
    #  Перерахунок статів після зміни апгрейдів
    # ─────────────────────────────────────────
    def _recalc_stats(self):
        cpc = 1.0   # базовий клік
        cps = 0.0
        for upg in self.upgrades:
            cpc += upg.click_bonus * upg.level
            cps += upg.passive     * upg.level
        self.coins_per_click = cpc
        self.coins_per_sec   = cps

    # ─────────────────────────────────────────
    #  Клік по монеті
    # ─────────────────────────────────────────
    def on_click(self, click_x: float, click_y: float) -> bool:
        """
        Викликається з ui/main коли гравець клікнув по монеті.
        Повертає False якщо перевищено ліміт кліків/сек.
        click_x, click_y — координати кліку (для розміщення popup).
        """
        if self._click_tokens < 1.0:
            return False   # занадто швидко
        self._click_tokens -= 1.0

        earned = self.coins_per_click
        self.coins        += earned
        self.total_earned += earned

        # анімація монети
        from settings import COIN_CLICK_SCALE
        self.coin_scale = COIN_CLICK_SCALE

        # спливаюче число
        self.popups.append(PopupNumber(click_x, click_y, earned))
        return True

    # ─────────────────────────────────────────
    #  Купівля апгрейду
    # ─────────────────────────────────────────
    def buy_upgrade(self, upgrade_id: str) -> bool:
        """
        Повертає True якщо покупка пройшла успішно, False — якщо монет мало.
        """
        upg = self._get_upgrade(upgrade_id)
        if upg is None:
            return False

        cost = upg.current_cost
        if self.coins < cost:
            return False

        self.coins -= cost
        upg.level  += 1
        self._recalc_stats()
        return True

    # ─────────────────────────────────────────
    #  Оновлення стану (кожен кадр)
    # ─────────────────────────────────────────
    def update(self, dt: float):
        """
        dt — час у секундах з попереднього кадру.
        Нараховує пасивний дохід, оновлює анімації.
        """
        # поповнення токенів кліків (до максимуму)
        self._click_tokens = min(
            self._click_tokens + MAX_CLICKS_PER_SEC * dt,
            MAX_CLICKS_PER_SEC
        )

        # пасивний дохід
        if self.coins_per_sec > 0:
            earned = self.coins_per_sec * dt
            self.coins        += earned
            self.total_earned += earned

        # анімація монети — плавне повернення до 1.0
        from settings import COIN_ANIM_SPEED
        if self.coin_scale > 1.0:
            self.coin_scale -= COIN_ANIM_SPEED
            if self.coin_scale < 1.0:
                self.coin_scale = 1.0

        # оновлення та видалення мертвих popup'ів
        for p in self.popups:
            p.update(dt)
        self.popups = [p for p in self.popups if p.alive]

    # ─────────────────────────────────────────
    #  Офлайн-прогрес
    # ─────────────────────────────────────────
    def apply_offline_income(self, seconds_away: float):
        """
        Нараховує монети за час, поки гра була закрита.
        Обмежено OFFLINE_INCOME_CAP секундами.
        """
        seconds_away = min(seconds_away, OFFLINE_INCOME_CAP)
        if self.coins_per_sec <= 0 or seconds_away <= 0:
            return 0.0

        earned = self.coins_per_sec * seconds_away
        self.coins        += earned
        self.total_earned += earned
        return earned   # повертаємо для показу повідомлення в UI

    # ─────────────────────────────────────────
    #  Серіалізація (для save_load.py)
    # ─────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "coins":        self.coins,
            "total_earned": self.total_earned,
            "timestamp":    time.time(),
            "upgrades":     [u.to_dict() for u in self.upgrades],
            "sound_on":     self.sound_on,
            "music_on":     self.music_on,
        }

    def from_dict(self, data: dict):
        """Завантажує стан з словника (розпарсеного JSON)."""
        self.coins        = float(data.get("coins", 0))
        self.total_earned = float(data.get("total_earned", 0))
        self.sound_on     = bool(data.get("sound_on", True))
        self.music_on     = bool(data.get("music_on", True))

        # відновлення рівнів апгрейдів
        saved_levels = {u["id"]: u["level"] for u in data.get("upgrades", [])}
        for upg in self.upgrades:
            upg.level = saved_levels.get(upg.id, 0)

        self._recalc_stats()

        # офлайн-прогрес
        saved_time = data.get("timestamp")
        if saved_time:
            seconds_away = time.time() - float(saved_time)
            offline_earned = self.apply_offline_income(seconds_away)
            return offline_earned   # скільки дав офлайн (для UI-повідомлення)
        return 0.0

    # ─────────────────────────────────────────
    #  Хелпери
    # ─────────────────────────────────────────
    def _get_upgrade(self, upgrade_id: str):
        for upg in self.upgrades:
            if upg.id == upgrade_id:
                return upg
        return None

    @staticmethod
    def format_number(n: float) -> str:
        """Скорочує великі числа: 1500 → '1.5K', 2000000 → '2.0M' тощо."""
        if n < 1_000:
            return str(int(n))
        elif n < 1_000_000:
            return f"{n / 1_000:.1f}K"
        elif n < 1_000_000_000:
            return f"{n / 1_000_000:.1f}M"
        elif n < 1_000_000_000_000:
            return f"{n / 1_000_000_000:.1f}B"
        else:
            return f"{n / 1_000_000_000_000:.1f}T"