# ─────────────────────────────────────────────
#  main.py  —  точка входу, ігровий цикл
# ─────────────────────────────────────────────
import sys
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    GAME_AREA_WIDTH, TOP_BAR_HEIGHT,
    COIN_BASE_RADIUS, COIN_GLOW_RADIUS,
    TAB_CLICK, TAB_WORKERS, TAB_SETTINGS,
    MUSIC_FILE, COLOR_BG,
)
from game      import GameState
from save_load import save, load, delete_save
import ui


# ══════════════════════════════════════════════
#  Ініціалізація
# ══════════════════════════════════════════════
def init():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock  = pygame.time.Clock()
    ui.init_fonts()
    ui.init_images()
    return screen, clock


# ══════════════════════════════════════════════
#  Музика і звуки
# ══════════════════════════════════════════════
def start_music():
    """Запускає фонову музику якщо файл існує."""
    try:
        pygame.mixer.music.load(MUSIC_FILE)   # шлях змінюється в settings.py
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)            # -1 = нескінченний loop
    except Exception:
        pass   # файл не знайдено — без музики


def load_sounds() -> dict:
    sounds = {}
    for name, path in [("click", "assets/sounds/click.wav"),
                        ("buy",   "assets/sounds/buy.wav")]:
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(0.4)
            sounds[name] = s
        except Exception:
            sounds[name] = None
    return sounds


def play(sounds, name, game):
    if not game.sound_on:
        return
    s = sounds.get(name)
    if s:
        s.play()


# ══════════════════════════════════════════════
#  Обробка подій
# ══════════════════════════════════════════════
def handle_events(game: GameState, sounds: dict,
                  current_tab: str) -> tuple[bool, str]:
    """Повертає (running, current_tab)."""

    for event in pygame.event.get():

        # ── Закриття вікна ────────────────────
        if event.type == pygame.QUIT:
            save(game)
            return False, current_tab

        # ── Клавіатура ────────────────────────
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save(game)

        # ── Скрол колесом ─────────────────────
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx >= GAME_AREA_WIDTH and current_tab in (TAB_CLICK, TAB_WORKERS):
                tab_key = "click" if current_tab == TAB_CLICK else "worker"
                ui.scroll_upgrades(tab_key, -event.y)  # event.y: +вгору, -вниз

        # ── Клік мишею ────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # -- вкладки (завжди першочергово) --
            tab = ui.get_clicked_tab(mx, my)
            if tab:
                if tab != current_tab:
                    ui.set_confirm_mode(False)  # скидаємо підтвердження при зміні вкладки
                current_tab = tab
                continue

            # -- Settings: тогли і кнопка видалення --
            if current_tab == TAB_SETTINGS:
                # спочатку перевіряємо кнопку видалення
                del_action = ui.get_clicked_delete(mx, my)
                if del_action == "delete":
                    ui.set_confirm_mode(True)
                    continue
                elif del_action == "yes":
                    delete_save()
                    game.__init__()              # повний скид стану
                    ui.set_confirm_mode(False)
                    continue
                elif del_action == "no":
                    ui.set_confirm_mode(False)
                    continue

                # тогли
                tog = ui.get_clicked_toggle(mx, my)
                if tog == "sound":
                    game.sound_on = not game.sound_on
                elif tog == "music":
                    game.music_on = not game.music_on
                    if game.music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                continue

            # -- Клік по монеті (ліва зона) --
            if mx < GAME_AREA_WIDTH and my > TOP_BAR_HEIGHT:
                cx, cy = ui.get_coin_center()
                dist = ((mx - cx) ** 2 + (my - cy) ** 2) ** 0.5
                if dist <= COIN_GLOW_RADIUS * game.coin_scale:
                    if game.on_click(mx, my):       # False = ліміт перевищено
                        play(sounds, "click", game)
                continue

            # -- Апгрейди (права зона) --
            if mx >= GAME_AREA_WIDTH:
                uid = ui.get_clicked_upgrade(mx, my)
                if uid and game.buy_upgrade(uid):
                    play(sounds, "buy", game)

    return True, current_tab


# ══════════════════════════════════════════════
#  Автозбереження
# ══════════════════════════════════════════════
_save_timer = 0.0
AUTOSAVE_INTERVAL = 30.0


def maybe_autosave(game, dt):
    global _save_timer
    _save_timer += dt
    if _save_timer >= AUTOSAVE_INTERVAL:
        save(game)
        _save_timer = 0.0


# ══════════════════════════════════════════════
#  Головний цикл
# ══════════════════════════════════════════════
def main():
    screen, clock = init()
    sounds = load_sounds()
    start_music()

    game = GameState()
    offline_earned = load(game)
    ui.show_offline_message(offline_earned, game.format_number)

    # музика — враховуємо збережене налаштування
    if not game.music_on:
        pygame.mixer.music.pause()

    current_tab = TAB_CLICK
    running     = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)

        running, current_tab = handle_events(game, sounds, current_tab)
        game.update(dt)
        maybe_autosave(game, dt)

        # ── Рендеринг ─────────────────────────
        screen.fill(COLOR_BG)
        ui.draw_top_bar(screen, game)
        ui.draw_game_area(screen, game)
        ui.draw_panel(screen, game, current_tab)
        ui.draw_offline_message(screen, dt)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()