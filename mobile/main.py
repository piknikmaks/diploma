# ─────────────────────────────────────────────
#  main.py  —  точка входу мобiльної / Android версiї
# ─────────────────────────────────────────────
from __future__ import annotations

import sys
import os
import time
import traceback

# ── Android: SDL env ДО будь-якого import pygame ──
def _is_android() -> bool:
    return bool(
        os.environ.get("ANDROID_ARGUMENT")
        or os.environ.get("ANDROID_BOOTLOGO")
        or os.environ.get("ANDROID_PRIVATE")
    )


def _setup_android_sdl_env():
    if not _is_android():
        return
    os.environ.setdefault("SDL_AUDIODRIVER", "android")
    os.environ.setdefault("SDL_VIDEODRIVER", "android")
    os.environ.setdefault("SDL_ANDROID_BLOCK_ON_PAUSE", "1")
    os.environ.setdefault("SDL_ACCELEROMETER_AS_JOYSTICK", "0")


_setup_android_sdl_env()


def _boot_file_log(msg: str):
    """Запис у файл на пристрої — видно навіть якщо logcat фільтрує print."""
    line = msg + "\n"
    candidates = []
    for key in ("ANDROID_PRIVATE", "ANDROID_APP_PATH"):
        v = os.environ.get(key)
        if v:
            candidates.append(v)
    candidates.append("/data/data/org.test.myclicker/files")
    for base in candidates:
        try:
            if not os.path.isdir(base):
                continue
            with open(os.path.join(base, "clicker_boot.log"), "a", encoding="utf-8") as f:
                f.write(line)
            return
        except OSError:
            continue


def _android_log(msg: str):
    try:
        from jnius import autoclass
        autoclass("android.util.Log").i("Clicker", msg)
    except Exception:
        pass


def _android_display_metrics() -> tuple[int, int, float] | None:
    """
    Реальна роздільність екрана в пікселях і density (1.0 = mdpi).
    display.Info() / get_size() на Android часто повертають ~480×854.
    """
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        if activity is None:
            return None
        DisplayMetrics = autoclass("android.util.DisplayMetrics")
        metrics = DisplayMetrics()
        activity.getWindowManager().getDefaultDisplay().getRealMetrics(metrics)
        w = int(metrics.widthPixels)
        h = int(metrics.heightPixels)
        density = float(metrics.density)
        if w > 0 and h > 0:
            return w, h, density
    except Exception as e:
        _log(f"android metrics: {e}")
    return None


def _android_apply_display(pg, screen, metrics: tuple[int, int, float] | None):
    """Відкриває surface на повний екран і оновлює масштаб UI."""
    px_w, px_h, density = (0, 0, 1.0)
    if metrics:
        px_w, px_h, density = metrics

    if px_w > 0 and px_h > 0:
        try:
            screen = pg.display.set_mode((px_w, px_h))
        except Exception as e:
            _log(f"set_mode({px_w}x{px_h}) failed: {e}")
            try:
                screen = pg.display.set_mode((0, 0))
            except Exception:
                pass

    w, h = screen.get_size()
    if metrics and w > 0 and h > 0 and w < px_w * 0.85 and px_w >= 720:
        w, h = px_w, px_h

    ui.set_screen_size(w, h, density)
    import settings_mobile as screen_layout
    _log(
        f"display surface={screen.get_size()} layout={w}x{h} "
        f"scale={screen_layout.SCALE:.2f} density={density:.2f} "
        f"bar_h={screen_layout.RES_BAR_H}"
    )
    return screen


def _log(msg: str):
    """logcat (тег python / Clicker), файл clicker_boot.log, Android Log."""
    text = f"[Clicker] {msg}"
    print(text, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    _boot_file_log(text)
    _android_log(msg)


_log("main.py loaded")

# На Android чекаємо стабілізації Surface після splash (уникає hwui mutex crash)
if _is_android():
    _log("android: wait for surface")
    time.sleep(1.0)

pygame = None
ui = None


def _import_pygame():
    global pygame
    if pygame is not None:
        return pygame
    _log("importing pygame...")
    import pygame as pg
    pygame = pg
    _log(f"pygame {pg.version.ver}")
    if _is_android():
        if not pg.get_init():
            pg.init()
        _log("pygame init (android)")
    else:
        try:
            pg.mixer.pre_init(44100, -16, 2, 512)
        except Exception as e:
            _log(f"mixer pre_init skipped: {e}")
        pg.init()
    return pygame


def _import_app_modules():
    global ui, MOBILE_DEFAULT_W, MOBILE_DEFAULT_H, FPS, WINDOW_TITLE
    global TAB_HOME, TAB_CLICK, TAB_WORKERS, TAB_REBIRTH
    global TAB_ACHIEVEMENTS, TAB_STATS, TAB_SETTINGS, MUSIC_FILE, COLOR_BG
    global GameState, save, load, delete_save
    from settings_mobile import (
        MOBILE_DEFAULT_W as _W,
        MOBILE_DEFAULT_H as _H,
        FPS as _FPS,
        WINDOW_TITLE as _TITLE,
        TAB_HOME as _TH,
        TAB_CLICK as _TC,
        TAB_WORKERS as _TW,
        TAB_REBIRTH as _TR,
        TAB_ACHIEVEMENTS as _TA,
        TAB_STATS as _TS,
        TAB_SETTINGS as _TSET,
        MUSIC_FILE as _MUSIC,
        COLOR_BG as _BG,
    )
    MOBILE_DEFAULT_W, MOBILE_DEFAULT_H = _W, _H
    FPS, WINDOW_TITLE = _FPS, _TITLE
    TAB_HOME, TAB_CLICK, TAB_WORKERS = _TH, _TC, _TW
    TAB_REBIRTH, TAB_ACHIEVEMENTS = _TR, _TA
    TAB_STATS, TAB_SETTINGS = _TS, _TSET
    MUSIC_FILE, COLOR_BG = _MUSIC, _BG
    from game import GameState as _GS
    from save_load import save as _save, load as _load, delete_save as _del
    GameState, save, load, delete_save = _GS, _save, _load, _del
    import ui_mobile as ui_mod
    ui = ui_mod
    _log("modules imported")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# ══════════════════════════════════════════════
#  Iнiцiалiзацiя
# ══════════════════════════════════════════════
def init() -> tuple:
    """Iнiцiалiзує pygame, вiкно, шрифти, зображення."""
    pg = _import_pygame()
    if not _is_android():
        try:
            pg.mixer.init()
        except Exception as e:
            _log(f"mixer init skipped: {e}")

    # На реальному Android-пристрої set_mode((0,0)) вiдкриє повний екран.
    # На ПК — використовуємо фiксований розмiр для тестування.
    from settings_mobile import desktop_window_size

    is_android = _is_android()
    metrics = _android_display_metrics() if is_android else None
    try:
        if is_android:
            if metrics:
                screen = pg.display.set_mode((metrics[0], metrics[1]))
            else:
                screen = pg.display.set_mode((0, 0))
        else:
            info = pg.display.Info()
            ww, hh = desktop_window_size(info.current_w, info.current_h)
            screen = pg.display.set_mode((ww, hh), pg.RESIZABLE)
    except Exception as e:
        _log(f"set_mode primary failed: {e}")
        try:
            screen = pg.display.set_mode((MOBILE_DEFAULT_W, MOBILE_DEFAULT_H))
        except Exception:
            screen = pg.display.set_mode((MOBILE_DEFAULT_W, MOBILE_DEFAULT_H))

    pg.display.set_caption(WINDOW_TITLE)

    if is_android:
        screen = _android_apply_display(pg, screen, metrics)
    else:
        w, h = screen.get_size()
        ui.set_screen_size(w, h)

    clock = pg.time.Clock()
    return screen, clock


def start_music():
    """Запускає фонову музику якщо файл iснує."""
    pg = _import_pygame()
    try:
        if not pg.mixer.get_init():
            pg.mixer.init()
        pg.mixer.music.load(resource_path(MUSIC_FILE))
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)
    except Exception as e:
        _log(f"music skipped: {e}")


def load_sounds() -> dict:
    """Завантажує звуковi ефекти."""
    pg = _import_pygame()
    sounds = {}
    sound_files = {
        "click": ["assets/sounds/click.wav"],
        "buy":   ["assets/sounds/buy.wav", "assets/sounds/buy.mp3"],
    }
    for name, paths in sound_files.items():
        sounds[name] = None
        for path in paths:
            full = resource_path(path)
            if not os.path.exists(full):
                continue
            try:
                s = pg.mixer.Sound(full)
                s.set_volume(0.4)
                sounds[name] = s
                break
            except Exception as e:
                print(f"[audio] cannot load {path}: {e}")
    return sounds


def play(sounds: dict, name: str, game: GameState):
    """Грає звук якщо вiн увiмкнений у налаштуваннях."""
    if not game.sound_on:
        return
    s = sounds.get(name)
    if s:
        s.play()


# ══════════════════════════════════════════════
#  Стан дотику (для вiдрiзнення тапу вiд свайпу)
# ══════════════════════════════════════════════
class TouchState:
    """
    Зберiгає данi поточного дотику:
    початкову позицiю, час старту та поточне змiщення.
    Дозволяє вiдрiзнити тап (коротке натискання) вiд свайпу.
    """
    TAP_MAX_DIST  = 12    # максимальне змiщення щоб вважати тапом (px)
    TAP_MAX_TIME  = 0.3   # максимальний час тапу (сек)

    def __init__(self):
        self.active     = False
        self.start_x    = 0
        self.start_y    = 0
        self.cur_x      = 0
        self.cur_y      = 0
        self.start_time = 0.0
        self.duration   = 0.0

    def begin(self, x: int, y: int):
        self.active     = True
        self.start_x    = x;  self.cur_x = x
        self.start_y    = y;  self.cur_y = y
        self.start_time = _import_pygame().time.get_ticks() / 1000.0
        self.duration   = 0.0

    def move(self, x: int, y: int):
        self.cur_x = x
        self.cur_y = y
        self.duration = _import_pygame().time.get_ticks() / 1000.0 - self.start_time

    def end(self) -> bool:
        """Повертає True якщо дотик можна вважати тапом."""
        dx = abs(self.cur_x - self.start_x)
        dy = abs(self.cur_y - self.start_y)
        dist = (dx * dx + dy * dy) ** 0.5
        self.active = False
        max_d = ui._s(self.TAP_MAX_DIST) if ui else self.TAP_MAX_DIST
        return dist <= max_d and self.duration <= self.TAP_MAX_TIME

    @property
    def delta_y(self) -> float:
        return float(self.cur_y - self.start_y)

    @property
    def delta_x(self) -> float:
        return float(self.cur_x - self.start_x)


# ── Окремi стани дотику для рiзних зон ───────
_coin_touch    = TouchState()   # дотик у зонi монети
_list_touch    = TouchState()   # дотик у зонi списку апгрейдiв
_tabbar_touch  = TouchState()   # дотик у зонi бару вкладок
_slider_drag   = False          # чи тягнемо зараз слайдер гучностi


# ══════════════════════════════════════════════
#  Конвертацiя координат (Finger -> пiкселi)
# ══════════════════════════════════════════════
def finger_to_px(event, screen: pygame.Surface) -> tuple[int, int]:
    """
    Конвертує нормалiзованi координати FINGERDOWN/UP/MOTION
    (0.0 – 1.0) у пiксельнi координати екрану.
    """
    w, h = screen.get_size()
    return int(event.x * w), int(event.y * h)


# ══════════════════════════════════════════════
#  Обробка подiй
# ══════════════════════════════════════════════
def handle_events(game, sounds: dict,
                  current_tab: str,
                  screen):
    """
    Обробляє всi подiї pygame.
    Повертає (running, current_tab, screen).
    running=False означає вихiд з гри.
    """
    global _slider_drag
    pg = _import_pygame()

    for event in pg.event.get():

        # ── Закриття вiкна ────────────────────
        if event.type == pg.QUIT:
            save(game)
            return False, current_tab, screen

        if event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
            ui.set_screen_size(event.w, event.h)

        # ── Клавiатура (для тестування на ПК) ─
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_s:
                save(game)
            elif event.key == pg.K_ESCAPE:
                save(game)
                return False, current_tab, screen

        # ── Вiдпускання мишi / пальця (кiнець слайдера) ──
        if event.type in (pg.MOUSEBUTTONUP, pg.FINGERUP):
            _slider_drag = False

        # ─────────────────────────────────────────────────
        #  FINGER-подiї (реальний сенсорний екран)
        # ─────────────────────────────────────────────────
        if event.type == pg.FINGERDOWN:
            fx, fy = finger_to_px(event, screen)
            _handle_touch_begin(fx, fy, current_tab)

        elif event.type == pg.FINGERMOTION:
            fx, fy = finger_to_px(event, screen)
            current_tab = _handle_touch_move(fx, fy, current_tab, game, sounds)

        elif event.type == pg.FINGERUP:
            fx, fy = finger_to_px(event, screen)
            result = _handle_touch_end(fx, fy, current_tab, game, sounds)
            if result is False:
                return False, current_tab, screen
            if result is not None:
                current_tab = result

        # ─────────────────────────────────────────────────
        #  MOUSE-подiї (для тестування на ПК)
        # ─────────────────────────────────────────────────
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            _handle_touch_begin(mx, my, current_tab)
            _slider_drag = (
                current_tab == TAB_SETTINGS and ui.is_on_slider(mx, my))

        elif event.type == pg.MOUSEMOTION:
            if any(btn for btn in pg.mouse.get_pressed()):
                mx, my = event.pos
                current_tab = _handle_touch_move(mx, my, current_tab, game, sounds)

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            mx, my = event.pos
            result = _handle_touch_end(mx, my, current_tab, game, sounds)
            if result is False:
                return False, current_tab, screen
            if result is not None:
                current_tab = result

        # ── Скрол колесом мишi (для ПК) ──────
        elif event.type == pg.MOUSEWHEEL:
            if current_tab in (TAB_CLICK, TAB_WORKERS):
                typ = "click" if current_tab == TAB_CLICK else "worker"
                ui.scroll_upgrades(typ, float(-event.y * ui._s(25)))
                ui.clamp_upgrade_scroll(typ, game)

    return True, current_tab, screen


def _handle_touch_begin(x: int, y: int, current_tab: str):
    """Обробляє початок дотику: визначає в якiй зонi."""
    global _slider_drag

    import settings_mobile as screen_layout
    tab_bar_y = ui.H - screen_layout.TAB_BAR_H

    if y < screen_layout.RES_BAR_H:
        # бар ресурсiв — нiчого
        pass
    elif y >= tab_bar_y:
        # бар вкладок
        _tabbar_touch.begin(x, y)
    elif current_tab == TAB_HOME:
        # зона монети
        _coin_touch.begin(x, y)
    elif current_tab in (TAB_CLICK, TAB_WORKERS):
        # список апгрейдiв
        _list_touch.begin(x, y)
    elif current_tab == TAB_SETTINGS and ui.is_on_slider(x, y):
        # слайдер гучностi
        _slider_drag = True
    else:
        # iншi вкладки — просто тап
        _list_touch.begin(x, y)


def _handle_touch_move(x: int, y: int, current_tab: str,
                       game: GameState, sounds: dict) -> str:
    """Обробляє рух пальця: скрол списку або свайп вкладок."""
    global _slider_drag

    import settings_mobile as screen_layout
    tab_bar_y = ui.H - screen_layout.TAB_BAR_H

    if _slider_drag and current_tab == TAB_SETTINGS:
        # тягнемо слайдер
        vol = ui.slider_volume_at(x)
        if vol is not None:
            game.music_volume = vol
            try:
                _import_pygame().mixer.music.set_volume(vol)
            except Exception:
                pass

    elif _tabbar_touch.active and y >= tab_bar_y:
        # горизонтальний свайп по бару вкладок
        prev_x = _tabbar_touch.cur_x
        _tabbar_touch.move(x, y)
        dx = prev_x - x   # негативний = свайп вправо (до правих вкладок)
        ui.scroll_tab_bar(dx)

    elif _list_touch.active and current_tab in (TAB_CLICK, TAB_WORKERS):
        # вертикальний скрол списку апгрейдiв
        prev_y = _list_touch.cur_y
        _list_touch.move(x, y)
        dy = prev_y - y   # негативний = свайп вниз (скрол вниз)
        typ = "click" if current_tab == TAB_CLICK else "worker"
        ui.scroll_upgrades(typ, dy)
        ui.clamp_upgrade_scroll(typ, game)

    elif _coin_touch.active and current_tab == TAB_HOME:
        _coin_touch.move(x, y)

    return current_tab


def _handle_touch_end(x: int, y: int, current_tab: str,
                      game: GameState, sounds: dict):
    """
    Обробляє кiнець дотику.
    Якщо це тап (коротке натискання) — виконує дiю.
    Повертає новий current_tab або False (вийти) або None.
    """
    import settings_mobile as screen_layout
    tab_bar_y = ui.H - screen_layout.TAB_BAR_H

    # -- дiалог кiнця гри (поверх усього) --
    if game.show_end_dialog:
        action = ui.get_end_dialog_hit(x, y)
        if action == "quit":
            save(game)
            return False
        elif action == "continue":
            game.show_end_dialog = False
            game.game_completed  = False
        return current_tab

    # -- бар вкладок: тап = перемикання вкладки --
    if _tabbar_touch.active:
        is_tap = _tabbar_touch.end()
        if is_tap and y >= tab_bar_y:
            new_tab = ui.get_tab_at(x, y)
            if new_tab and new_tab != current_tab:
                ui.set_confirm_mode(False)
                ui.set_endgame_confirm(False)
                return new_tab
        return current_tab

    # -- монета (головна вкладка) --
    if _coin_touch.active and current_tab == TAB_HOME:
        is_tap = _coin_touch.end()
        if is_tap:
            cx, cy, rad = ui.get_coin_hit(game)
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= rad:
                if game.on_click(x, y):
                    play(sounds, "click", game)
        return current_tab

    # -- список апгрейдiв --
    if _list_touch.active and current_tab in (TAB_CLICK, TAB_WORKERS):
        is_tap = _list_touch.end()
        if is_tap:
            uid = ui.get_upgrade_at(x, y)
            if uid and game.buy_upgrade(uid):
                play(sounds, "buy", game)
        return current_tab

    # -- перерождення --
    if current_tab == TAB_REBIRTH:
        _list_touch.end()
        # кiнець гри
        eg = ui.get_endgame_hit(x, y)
        if eg == "endgame":
            ui.set_endgame_confirm(True)
        elif eg == "yes":
            if game.do_end_game():
                ui.set_endgame_confirm(False)
                ui.start_end_animation()
        elif eg == "no":
            ui.set_endgame_confirm(False)
        # перерождення
        elif ui.get_rebirth_hit(x, y):
            if game.do_rebirth():
                play(sounds, "buy", game)
        return current_tab

    # -- налаштування --
    if current_tab == TAB_SETTINGS:
        _list_touch.end()
        if not ui.is_on_slider(x, y):
            del_a = ui.get_delete_hit(x, y)
            if del_a == "delete":
                ui.set_confirm_mode(True)
            elif del_a == "yes":
                delete_save()
                game.__init__()
                ui.set_confirm_mode(False)
            elif del_a == "no":
                ui.set_confirm_mode(False)
            else:
                tog = ui.get_toggle_hit(x, y)
                if tog == "sound":
                    game.sound_on = not game.sound_on
        return current_tab

    # iншi вкладки — просто скидаємо стан дотику
    _list_touch.end()
    return current_tab


# ══════════════════════════════════════════════
#  Автозбереження
# ══════════════════════════════════════════════
_save_timer  = 0.0
AUTOSAVE_SEC = 30.0


def maybe_autosave(game: GameState, dt: float):
    global _save_timer
    _save_timer += dt
    if _save_timer >= AUTOSAVE_SEC:
        save(game)
        _save_timer = 0.0


# ══════════════════════════════════════════════
#  Рендеринг
# ══════════════════════════════════════════════
def render(screen, game, current_tab: str, dt: float):
    """Малює весь кадр."""
    screen.fill(COLOR_BG)

    # -- вибiр контенту за вкладкою --
    if current_tab == TAB_HOME:
        ui.draw_home(screen, game)
    elif current_tab == TAB_CLICK:
        ui.draw_upgrades(screen, game, "click")
    elif current_tab == TAB_WORKERS:
        ui.draw_upgrades(screen, game, "worker")
    elif current_tab == TAB_REBIRTH:
        ui.draw_rebirth(screen, game)
    elif current_tab == TAB_ACHIEVEMENTS:
        ui.draw_achievements(screen, game)
    elif current_tab == TAB_STATS:
        ui.draw_stats(screen, game)
    elif current_tab == TAB_SETTINGS:
        ui.draw_settings(screen, game)

    # -- завжди поверх контенту --
    ui.draw_res_bar(screen, game)
    ui.draw_tab_bar(screen, current_tab)
    ui.draw_offline_message(screen, dt)

    # -- кiнцева анiмацiя (якщо активна) --
    if game.end_anim_timer > 0 or game.show_end_dialog:
        ui.draw_end_animation(screen, game)

    _import_pygame().display.flip()


# ══════════════════════════════════════════════
#  Головна функцiя
# ══════════════════════════════════════════════
def _run_game():
    _log("starting game loop")
    _import_pygame()
    _import_app_modules()
    screen, clock = init()
    sounds = load_sounds()
    start_music()

    game = GameState()
    offline_earned = load(game)
    ui.show_offline_message(offline_earned, game.format_number)

    try:
        _import_pygame().mixer.music.set_volume(game.music_volume)
    except Exception:
        pass

    current_tab = TAB_HOME
    running     = True
    _android_layout_retries = 5 if _is_android() else 0

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)

        if _android_layout_retries > 0:
            _android_layout_retries -= 1
            m = _android_display_metrics()
            if m:
                import settings_mobile as screen_layout
                if screen_layout.SCALE < 1.5 or screen.get_size()[0] < 720:
                    screen = _android_apply_display(_import_pygame(), screen, m)

        running, current_tab, screen = handle_events(game, sounds, current_tab, screen)
        game.update(dt)
        maybe_autosave(game, dt)
        ui.tick_achievement_banner(game, dt)

        if game.end_anim_timer > 0 or game.show_end_dialog:
            ui.update_end_animation(dt)

        render(screen, game, current_tab, dt)

    _import_pygame().quit()


def main():
    try:
        _run_game()
    except Exception:
        _log("FATAL: uncaught exception in main")
        traceback.print_exc()
        raise
    sys.exit()


if __name__ == "__main__":
    main()