# ─────────────────────────────────────────────
#  main.py  —  точка входу, ігровий цикл
# ─────────────────────────────────────────────
import sys
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    GAME_AREA_WIDTH, TOP_BAR_HEIGHT, COIN_GLOW_RADIUS,
    TAB_CLICK, TAB_WORKERS, TAB_REBIRTH, TAB_SETTINGS,
    MUSIC_FILE, COLOR_BG,
)
from game      import GameState
from save_load import save, load, delete_save
import ui


def init():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock  = pygame.time.Clock()
    ui.init_fonts()
    ui.init_images()
    return screen, clock


def start_music():
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


def load_sounds():
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
    if not game.sound_on: return
    s = sounds.get(name)
    if s: s.play()


# ══════════════════════════════════════════════
#  Обробка подій
# ══════════════════════════════════════════════
_slider_dragging = False   # чи тягнемо слайдер зараз

def handle_events(game: GameState, sounds: dict,
                  current_tab: str) -> tuple[bool, str]:
    global _slider_dragging

    for event in pygame.event.get():

        # ── Закриття ─────────────────────────
        if event.type == pygame.QUIT:
            save(game); return False, current_tab

        # ── Клавіатура ───────────────────────
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save(game)

        # ── Відпускання кнопки миші ──────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            _slider_dragging = False

        # ── Рух миші (слайдер гучності) ──────
        if event.type == pygame.MOUSEMOTION and _slider_dragging:
            mx, _ = event.pos
            if current_tab == TAB_SETTINGS:
                vol = ui.slider_volume_at(mx)
                if vol is not None:
                    game.music_volume = vol
                    try: pygame.mixer.music.set_volume(vol)
                    except: pass

        # ── Скрол колесом ────────────────────
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx >= GAME_AREA_WIDTH and current_tab in (TAB_CLICK, TAB_WORKERS):
                key = "click" if current_tab == TAB_CLICK else "worker"
                ui.scroll_upgrades(key, -event.y)

        # ── Клік ─────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # ── Діалог кінця гри (поверх усього) ──
            if game.show_end_dialog:
                action = ui.get_clicked_end_dialog(mx, my)
                if action == "quit":
                    save(game); return False, current_tab
                elif action == "continue":
                    game.show_end_dialog = False
                    game.game_completed  = False
                continue   # поки діалог відкритий — ігноруємо все інше

            # ── Вкладки ──────────────────────
            tab = ui.get_clicked_tab(mx, my)
            if tab:
                if tab != current_tab:
                    ui.set_confirm_mode(False)
                    ui.set_endgame_confirm(False)
                current_tab = tab
                continue

            # ────────────────────────────────────
            #  ЛІВА ЗОНА (монета) — завжди перша!
            # ────────────────────────────────────
            if mx < GAME_AREA_WIDTH and my > TOP_BAR_HEIGHT:
                cx, cy = ui.get_coin_center()
                dist = ((mx-cx)**2 + (my-cy)**2)**0.5
                if dist <= COIN_GLOW_RADIUS * game.coin_scale:
                    if game.on_click(mx, my):
                        play(sounds, "click", game)
                continue

            # ────────────────────────────────────
            #  ПРАВА ЗОНА — залежно від вкладки
            # ────────────────────────────────────
            if mx < GAME_AREA_WIDTH:
                continue   # клік між зонами — ігноруємо

            # ── Налаштування ─────────────────
            if current_tab == TAB_SETTINGS:
                # слайдер гучності
                if ui.is_on_slider(mx, my):
                    _slider_dragging = True
                    vol = ui.slider_volume_at(mx)
                    if vol is not None:
                        game.music_volume = vol
                        try: pygame.mixer.music.set_volume(vol)
                        except: pass
                    continue

                # кнопка видалення
                del_action = ui.get_clicked_delete(mx, my)
                if del_action == "delete":
                    ui.set_confirm_mode(True); continue
                elif del_action == "yes":
                    delete_save(); game.__init__()
                    ui.set_confirm_mode(False); continue
                elif del_action == "no":
                    ui.set_confirm_mode(False); continue

                # тогл звуку
                tog = ui.get_clicked_toggle(mx, my)
                if tog == "sound":
                    game.sound_on = not game.sound_on
                continue

            # ── Перерождення ─────────────────
            elif current_tab == TAB_REBIRTH:
                # кінець гри
                eg = ui.get_clicked_endgame(mx, my)
                if eg == "endgame":
                    ui.set_endgame_confirm(True); continue
                elif eg == "yes":
                    if game.do_end_game():
                        ui.set_endgame_confirm(False)
                        ui.start_end_animation()
                    continue
                elif eg == "no":
                    ui.set_endgame_confirm(False); continue

                # перерождення
                if ui.get_clicked_rebirth(mx, my):
                    if game.do_rebirth():
                        play(sounds, "buy", game)
                continue

            # ── Апгрейди ─────────────────────
            else:
                uid = ui.get_clicked_upgrade(mx, my)
                if uid and game.buy_upgrade(uid):
                    play(sounds, "buy", game)

    return True, current_tab


# ══════════════════════════════════════════════
_save_timer = 0.0; AUTOSAVE = 30.0

def maybe_autosave(game, dt):
    global _save_timer
    _save_timer += dt
    if _save_timer >= AUTOSAVE:
        save(game); _save_timer = 0.0


# ══════════════════════════════════════════════
def main():
    screen, clock = init()
    sounds = load_sounds()
    start_music()

    game = GameState()
    offline_earned = load(game)
    ui.show_offline_message(offline_earned, game.format_number)

    # встановлюємо збережену гучність
    try: pygame.mixer.music.set_volume(game.music_volume)
    except: pass

    current_tab = TAB_CLICK
    running     = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)

        running, current_tab = handle_events(game, sounds, current_tab)
        game.update(dt)
        maybe_autosave(game, dt)
        ui.tick_achievement_banner(game, dt)

        # оновлення частинок кінцевої анімації
        if game.end_anim_timer > 0 or game.show_end_dialog:
            ui.update_end_animation(dt)

        # ── Рендеринг ─────────────────────────
        screen.fill(COLOR_BG)
        ui.draw_top_bar(screen, game)
        ui.draw_game_area(screen, game)
        ui.draw_panel(screen, game, current_tab)
        ui.draw_offline_message(screen, dt)

        # кінцева анімація поверх всього
        if game.end_anim_timer > 0 or game.show_end_dialog:
            ui.draw_end_animation(screen, game)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()