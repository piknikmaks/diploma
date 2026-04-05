# ─────────────────────────────────────────────
#  settings.py  —  усі константи проекту
# ─────────────────────────────────────────────

# ── Вікно ─────────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
FPS           = 60
WINDOW_TITLE  = "Clicker Game"

# ── Розподіл екрану ───────────────────────────
TOP_BAR_HEIGHT   = 70
GAME_AREA_WIDTH  = int(WINDOW_WIDTH * 0.60)
PANEL_WIDTH      = WINDOW_WIDTH - GAME_AREA_WIDTH

# ── Вкладки правої панелі ─────────────────────
TAB_CLICK        = "click"
TAB_WORKERS      = "workers"
TAB_REBIRTH      = "rebirth"
TAB_ACHIEVEMENTS = "achievements"
TAB_STATS        = "stats"
TAB_SETTINGS     = "settings"
TABS = [TAB_CLICK, TAB_WORKERS, TAB_REBIRTH, TAB_ACHIEVEMENTS, TAB_STATS, TAB_SETTINGS]
TAB_BAR_HEIGHT = 68   # трохи менше — 6 вкладок

# ── Кольори — світла тема ─────────────────────
COLOR_BG             = (220, 220, 220)
COLOR_TOP_BAR        = (245, 245, 245)
COLOR_TOP_BAR_BORDER = (200, 200, 200)
COLOR_PANEL_BG       = (195, 195, 195)
COLOR_PANEL_BORDER   = (170, 170, 170)

COLOR_TAB_ACTIVE     = (245, 245, 245)
COLOR_TAB_INACTIVE   = (180, 180, 180)
COLOR_TAB_HOVER      = (210, 210, 210)
COLOR_TAB_BORDER     = (155, 155, 155)

COLOR_TEXT           = (30,  30,  30)
COLOR_TEXT_DIM       = (110, 110, 110)
COLOR_TEXT_LOCKED    = (160, 160, 160)

COLOR_COIN_VAL       = (30,  30,  30)
COLOR_PASSIVE        = (60, 130, 200)
COLOR_CPC            = (100, 100, 100)

COLOR_BTN_NORMAL     = (235, 235, 235)
COLOR_BTN_HOVER      = (255, 255, 255)
COLOR_BTN_LOCKED     = (210, 210, 210)
COLOR_BTN_BORDER     = (190, 190, 190)
COLOR_BTN_BORDER_HOV = (140, 180, 255)

COLOR_POPUP          = (200, 140, 0)

COLOR_TOGGLE_ON      = (80,  180,  80)
COLOR_TOGGLE_OFF     = (180, 180, 180)
COLOR_TOGGLE_KNOB    = (255, 255, 255)
COLOR_DELETE_BTN     = (200,  60,  60)
COLOR_DELETE_CONFIRM = (220,  30,  30)
COLOR_DELETE_TEXT    = (255, 255, 255)

# Перерождення
COLOR_REBIRTH_BTN    = (140,  80, 200)   # фіолетовий
COLOR_REBIRTH_HOVER  = (160, 100, 220)
COLOR_REBIRTH_LOCKED = (170, 170, 185)
COLOR_REBIRTH_TEXT   = (255, 255, 255)
COLOR_REBIRTH_GLOW   = (180, 130, 255)

# Досягнення
COLOR_ACH_UNLOCKED   = (255, 215,   0)   # золоте
COLOR_ACH_LOCKED     = (200, 200, 200)
COLOR_ACH_BORDER_ON  = (200, 160,   0)
COLOR_ACH_BORDER_OFF = (160, 160, 160)

# ── Монета / діамант ──────────────────────────
COIN_BASE_RADIUS    = 100
COIN_CLICK_SCALE    = 1.07
COIN_ANIM_SPEED     = 0.12
COIN_GLOW_RADIUS    = 130
# Шаблон імені файлу: coin_0.png, coin_1.png, ...
COIN_IMAGE_TEMPLATE = "assets/images/coin_{}.png"

# ── Спливаючі числа ───────────────────────────
POPUP_LIFETIME  = 0.85
POPUP_SPEED     = 85

# ── Збереження / аудіо ────────────────────────
MUSIC_FILE          = "assets/sounds/music.ogg"
MAX_CLICKS_PER_SEC  = 20
SAVE_FILE           = "save.json"
OFFLINE_INCOME_CAP  = 4 * 60 * 60

# ── Перерождення ──────────────────────────────
REBIRTH_BASE_COST   = 10_000_000   # ціна першого перерождення

# ── Досягнення ────────────────────────────────
# condition_type: "total_earned" | "total_clicks" | "rebirths" | "upgrade_level"
# condition_value: число або {"upgrade_id": ..., "level": ...}
ACHIEVEMENTS = [
    # --- БАГАТСТВО (Total Earned) ---
    {
        "id": "first_coin",
        "name": "Перший крок",
        "desc": "Заробити 100 монет",
        "icon": "assets/images/icons/ach_coin_1.png",
        "condition_type": "total_earned",
        "condition_value": 100,
    },
    {
        "id": "thousandaire",
        "name": "Тисячник",
        "desc": "Заробити 10 000 монет",
        "icon": "assets/images/icons/ach_coin_2.png",
        "condition_type": "total_earned",
        "condition_value": 10_000,
    },
    {
        "id": "millionaire",
        "name": "Мільйонер",
        "desc": "Заробити 1 000 000 монет",
        "icon": "assets/images/icons/ach_star_1.png",
        "condition_type": "total_earned",
        "condition_value": 1_000_000,
    },
    {
        "id": "billionaire",
        "name": "Мільярдер",
        "desc": "Заробити 1 000 000 000 монет",
        "icon": "assets/images/icons/ach_star_2.png",
        "condition_type": "total_earned",
        "condition_value": 1_000_000_000,
    },
    {
        "id": "trillionaire",
        "name": "Трильйонер",
        "desc": "Заробити 1 000 000 000 000 монет",
        "icon": "assets/images/icons/ach_star_3.png",
        "condition_type": "total_earned",
        "condition_value": 1_000_000_000_000,
    },

    # --- КЛІКИ (Total Clicks) ---
    {
        "id": "clicker_100",
        "name": "Клікер",
        "desc": "Зробити 100 кліків",
        "icon": "assets/images/icons/ach_click_1.png",
        "condition_type": "total_clicks",
        "condition_value": 100,
    },
    {
        "id": "clicker_1000",
        "name": "Невтомний",
        "desc": "Зробити 1 000 кліків",
        "icon": "assets/images/icons/ach_click_2.png",
        "condition_type": "total_clicks",
        "condition_value": 1_000,
    },
    {
        "id": "clicker_10000",
        "name": "Машина кліків",
        "desc": "Зробити 10 000 кліків",
        "icon": "assets/images/icons/ach_click_3.png",
        "condition_type": "total_clicks",
        "condition_value": 10_000,
    },
    {
        "id": "click_legend",
        "name": "Легенда кліку",
        "desc": "Зробити 100 000 кліків",
        "icon": "assets/images/icons/ach_click_4.png",
        "condition_type": "total_clicks",
        "condition_value": 100_000,
    },

    # --- КЛЮЧОВІ АПГРЕЙДИ (Specific Upgrade Level) ---
    {
        "id": "first_worker",
        "name": "Перший найманець",
        "desc": "Найміть свого першого Помічника",
        "icon": "assets/images/icons/ach_worker.png",
        "condition_type": "upgrade_level",
        "condition_value": {"upgrade_id": "worker_1", "level": 1},
    },
    {
        "id": "alchemist",
        "name": "Майстер еліксирів",
        "desc": "Побудуйте Алхімічну лабораторію",
        "icon": "assets/images/icons/ach_alchemy.png",
        "condition_type": "upgrade_level",
        "condition_value": {"upgrade_id": "alchemy_lab", "level": 1},
    },
    {
        "id": "space_age",
        "name": "Космічна ера",
        "desc": "Запустіть Орбітальну станцію",
        "icon": "assets/images/icons/ach_space.png",
        "condition_type": "upgrade_level",
        "condition_value": {"upgrade_id": "orbital_station", "level": 1},
    },
    {
        "id": "world_creator_ach",
        "name": "Творець Всесвіту",
        "desc": "Побудуйте Генератор Світів",
        "icon": "assets/images/icons/ach_god.png",
        "condition_type": "upgrade_level",
        "condition_value": {"upgrade_id": "world_creator", "level": 1},
    },

    # --- ПЕРЕРОДЖЕННЯ (Rebirths) ---
    {
        "id": "first_rebirth",
        "name": "Нове народження",
        "desc": "Зробіть своє перше переродження",
        "icon": "assets/images/icons/ach_reb_1.png",
        "condition_type": "rebirths",
        "condition_value": 1,
    },
    {
        "id": "rebirth_5",
        "name": "Вічний мандрівник",
        "desc": "Переродитися 5 разів",
        "icon": "assets/images/icons/ach_reb_2.png",
        "condition_type": "rebirths",
        "condition_value": 5,
    },
    {
        "id": "rebirth_10",
        "name": "Майстер сансари",
        "desc": "Переродитися 10 разів",
        "icon": "assets/images/icons/ach_reb_3.png",
        "condition_type": "rebirths",
        "condition_value": 10,
    },

    # --- ФІНАЛЬНА МЕТА (The "End" Goal) ---
    {
        "id": "game_completed",
        "name": "Кінець гри?",
        "desc": "Досягти 1 квадрильйона монет та викупити Свободу",
        "icon": "assets/images/icons/ach_finish.png",
        "condition_type": "total_earned",
        "condition_value": 1_000_000_000_000_000,
    },
]

# ── Апгрейди ──────────────────────────────────
UPGRADES = [
    # --- АПГРЕЙДИ КЛІКУ (CLICK) ---
    {
        "id": "better_click", "name": "Покращена кирка",
        "description": "+5 до сили кліку", "base_cost": 10,
        "cost_mult": 1.5, "click_bonus": 5, "passive": 0,
        "type": "click", "icon": "assets/images/icons/pickaxe.png",
    },
    {
        "id": "double_click", "name": "Подвійний удар",
        "description": "+15 до сили кліку", "base_cost": 150,
        "cost_mult": 1.6, "click_bonus": 15, "passive": 0,
        "type": "click", "icon": "assets/images/icons/sword.png",
    },
    {
        "id": "golden_touch", "name": "Золотий дотик",
        "description": "+50 до сили кліку", "base_cost": 2000,
        "cost_mult": 1.8, "click_bonus": 50, "passive": 0,
        "type": "click", "icon": "assets/images/icons/gold.png",
    },
    {
        "id": "iron_glove", "name": "Залізна рукавиця",
        "description": "+120 до сили кліку", "base_cost": 5000,
        "cost_mult": 1.5, "click_bonus": 120, "passive": 0,
        "type": "click", "icon": "assets/images/icons/iron_glove.png",
    },
    {
        "id": "steel_pickaxe", "name": "Сталеве кайло",
        "description": "+300 до сили кліку", "base_cost": 15000,
        "cost_mult": 1.5, "click_bonus": 300, "passive": 0,
        "type": "click", "icon": "assets/images/icons/steel_pickaxe.png",
    },
    {
        "id": "diamond_drill", "name": "Алмазний бур",
        "description": "+800 до сили кліку", "base_cost": 45000,
        "cost_mult": 1.5, "click_bonus": 800, "passive": 0,
        "type": "click", "icon": "assets/images/icons/diamond_drill.png",
    },
    {
        "id": "rune_hammer", "name": "Рунічний молот",
        "description": "+2000 до сили кліку", "base_cost": 120000,
        "cost_mult": 1.55, "click_bonus": 2000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/rune_hammer.png",
    },
    {
        "id": "dynamite", "name": "Динаміт",
        "description": "+5000 до сили кліку", "base_cost": 400000,
        "cost_mult": 1.6, "click_bonus": 5000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/dynamite.png",
    },
    {
        "id": "laser_cutter", "name": "Лазерний різак",
        "description": "+15000 до сили кліку", "base_cost": 1500000,
        "cost_mult": 1.5, "click_bonus": 15000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/laser.png",
    },
    {
        "id": "plasma_drill", "name": "Плазмовий бур",
        "description": "+40000 до сили кліку", "base_cost": 5000000,
        "cost_mult": 1.55, "click_bonus": 40000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/plasma.png",
    },
    {
        "id": "magic_ring", "name": "Магічний перстень",
        "description": "+100 000 до сили кліку", "base_cost": 18000000,
        "cost_mult": 1.6, "click_bonus": 100000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/ring.png",
    },
    {
        "id": "heavy_excavator", "name": "Важкий екскаватор",
        "description": "+250 000 до сили кліку", "base_cost": 60000000,
        "cost_mult": 1.5, "click_bonus": 250000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/excavator.png",
    },
    {
        "id": "gravity_press", "name": "Гравітаційний прес",
        "description": "+800 000 до сили кліку", "base_cost": 200000000,
        "cost_mult": 1.55, "click_bonus": 800000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/gravity.png",
    },
    {
        "id": "quantum_arm", "name": "Квантовий маніпулятор",
        "description": "+2.5M до сили кліку", "base_cost": 800000000,
        "cost_mult": 1.6, "click_bonus": 2500000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/quantum.png",
    },
    {
        "id": "nano_bots_click", "name": "Рой нано-роботів",
        "description": "+8M до сили кліку", "base_cost": 3000000000,
        "cost_mult": 1.5, "click_bonus": 8000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/nanobots.png",
    },
    {
        "id": "antimatter_drill", "name": "Антиматерійний бур",
        "description": "+25M до сили кліку", "base_cost": 12000000000,
        "cost_mult": 1.55, "click_bonus": 25000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/antimatter.png",
    },
    {
        "id": "mini_black_hole", "name": "Міні-чорна діра",
        "description": "+80M до сили кліку", "base_cost": 50000000000,
        "cost_mult": 1.6, "click_bonus": 80000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/blackhole.png",
    },
    {
        "id": "solar_beam", "name": "Сонячний промінь",
        "description": "+250M до сили кліку", "base_cost": 200000000000,
        "cost_mult": 1.5, "click_bonus": 250000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/solar.png",
    },
    {
        "id": "meteor_strike", "name": "Метеоритний удар",
        "description": "+800M до сили кліку", "base_cost": 800000000000,
        "cost_mult": 1.55, "click_bonus": 800000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/meteor.png",
    },
    {
        "id": "titan_strength", "name": "Сила титана",
        "description": "+2.5B до сили кліку", "base_cost": 3000000000000,
        "cost_mult": 1.6, "click_bonus": 2500000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/titan.png",
    },
    {
        "id": "hyper_cutter", "name": "Гіперпросторовий різак",
        "description": "+10B до сили кліку", "base_cost": 12000000000000,
        "cost_mult": 1.5, "click_bonus": 10000000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/hyper.png",
    },
    {
        "id": "singularity", "name": "Сингулярність",
        "description": "+40B до сили кліку", "base_cost": 50000000000000,
        "cost_mult": 1.55, "click_bonus": 40000000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/singularity.png",
    },
    {
        "id": "star_destroyer", "name": "Зоряний руйнівник",
        "description": "+150B до сили кліку", "base_cost": 200000000000000,
        "cost_mult": 1.6, "click_bonus": 150000000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/star_destroyer.png",
    },
    {
        "id": "reality_rift", "name": "Розрив реальності",
        "description": "+600B до сили кліку", "base_cost": 800000000000000,
        "cost_mult": 1.5, "click_bonus": 600000000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/rift.png",
    },
    {
        "id": "god_power", "name": "Сила Творця",
        "description": "+2.5T до сили кліку", "base_cost": 3000000000000000,
        "cost_mult": 1.6, "click_bonus": 2500000000000, "passive": 0,
        "type": "click", "icon": "assets/images/icons/god.png",
    },

    # --- ПАСИВНІ АПГРЕЙДИ (WORKERS) ---
    {
        "id": "worker_1", "name": "Новачок-помічник",
        "description": "+1 монета/сек", "base_cost": 15,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 1,
        "type": "worker", "icon": "assets/images/icons/worker1.png",
    },
    {
        "id": "worker_2", "name": "Досвідчений шахтар",
        "description": "+5 монет/сек", "base_cost": 100,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 5,
        "type": "worker", "icon": "assets/images/icons/worker2.png",
    },
    {
        "id": "auto_clicker", "name": "Механічний автоклікер",
        "description": "+20 монет/сек", "base_cost": 500,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 20,
        "type": "worker", "icon": "assets/images/icons/auto.png",
    },
    {
        "id": "small_factory", "name": "Мала мануфактура",
        "description": "+80 монет/сек", "base_cost": 2500,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 80,
        "type": "worker", "icon": "assets/images/icons/small_factory.png",
    },
    {
        "id": "mine", "name": "Глибока шахта",
        "description": "+250 монет/сек", "base_cost": 10000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 250,
        "type": "worker", "icon": "assets/images/icons/mine.png",
    },
    {
        "id": "drilling_rig", "name": "Бурова установка",
        "description": "+800 монет/сек", "base_cost": 40000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 800,
        "type": "worker", "icon": "assets/images/icons/rig.png",
    },
    {
        "id": "steam_golem", "name": "Паровий голем",
        "description": "+2 500 монет/сек", "base_cost": 150000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 2500,
        "type": "worker", "icon": "assets/images/icons/golem.png",
    },
    {
        "id": "alchemy_lab", "name": "Алхімічна лабораторія",
        "description": "+8 000 монет/сек", "base_cost": 600000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 8000,
        "type": "worker", "icon": "assets/images/icons/alchemy.png",
    },
    {
        "id": "conveyor", "name": "Конвеєрна мережа",
        "description": "+25 000 монет/сек", "base_cost": 2500000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 25000,
        "type": "worker", "icon": "assets/images/icons/conveyor.png",
    },
    {
        "id": "robot_plant", "name": "Робототехнічний завод",
        "description": "+80 000 монет/сек", "base_cost": 10000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 80000,
        "type": "worker", "icon": "assets/images/icons/robot_plant.png",
    },
    {
        "id": "clone_center", "name": "Центр клонування",
        "description": "+250 000 монет/сек", "base_cost": 40000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 250000,
        "type": "worker", "icon": "assets/images/icons/clone.png",
    },
    {
        "id": "magic_tower", "name": "Магічна вежа",
        "description": "+800 000 монет/сек", "base_cost": 150000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 800000,
        "type": "worker", "icon": "assets/images/icons/tower.png",
    },
    {
        "id": "core_extractor", "name": "Екстрактор ядра",
        "description": "+2.5M монет/сек", "base_cost": 750000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 2500000,
        "type": "worker", "icon": "assets/images/icons/core.png",
    },
    {
        "id": "orbital_station", "name": "Орбітальна станція",
        "description": "+8M монет/сек", "base_cost": 3000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 8000000,
        "type": "worker", "icon": "assets/images/icons/orbital.png",
    },
    {
        "id": "moon_base", "name": "Місячна база",
        "description": "+25M монет/сек", "base_cost": 12000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 25000000,
        "type": "worker", "icon": "assets/images/icons/moon.png",
    },
    {
        "id": "mars_colony", "name": "Колонія на Марсі",
        "description": "+80M монет/сек", "base_cost": 50000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 80000000,
        "type": "worker", "icon": "assets/images/icons/mars.png",
    },
    {
        "id": "dyson_sphere", "name": "Сфера Дайсона",
        "description": "+250M монет/сек", "base_cost": 250000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 250000000,
        "type": "worker", "icon": "assets/images/icons/dyson.png",
    },
    {
        "id": "star_fleet", "name": "Зоряний флот",
        "description": "+800M монет/сек", "base_cost": 1200000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 800000000,
        "type": "worker", "icon": "assets/images/icons/fleet.png",
    },
    {
        "id": "galaxy_monopoly", "name": "Галактична монополія",
        "description": "+2.5B монет/сек", "base_cost": 6000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 2500000000,
        "type": "worker", "icon": "assets/images/icons/galaxy.png",
    },
    {
        "id": "ai_core", "name": "Надрозумний ШІ",
        "description": "+8B монет/сек", "base_cost": 30000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 8000000000,
        "type": "worker", "icon": "assets/images/icons/ai.png",
    },
    {
        "id": "multiverse_portal", "name": "Портал Мультивсесвіту",
        "description": "+25B монет/сек", "base_cost": 150000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 25000000000,
        "type": "worker", "icon": "assets/images/icons/portal.png",
    },
    {
        "id": "time_machine", "name": "Машина часу",
        "description": "+80B монет/сек", "base_cost": 800000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 80000000000,
        "type": "worker", "icon": "assets/images/icons/time.png",
    },
    {
        "id": "quantum_pc", "name": "Квантовий симулятор",
        "description": "+250B монет/сек", "base_cost": 4000000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 250000000000,
        "type": "worker", "icon": "assets/images/icons/quantum_pc.png",
    },
    {
        "id": "matter_harvester", "name": "Збирач темної матерії",
        "description": "+800B монет/сек", "base_cost": 25000000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 800000000000,
        "type": "worker", "icon": "assets/images/icons/dark_matter.png",
    },
    {
        "id": "world_creator", "name": "Генератор Світів",
        "description": "+2.5T монет/сек", "base_cost": 150000000000000000,
        "cost_mult": 1.15, "click_bonus": 0, "passive": 2500000000000,
        "type": "worker", "icon": "assets/images/icons/world.png",
    }
]