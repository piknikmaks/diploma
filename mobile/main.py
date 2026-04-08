# ─────────────────────────────────────────────
#  main_mobile.py  —  точка входу мобiльної версiї
#
#  Використовує спiльнi: game.py, save_load.py, settings.py
#  Власнi: settings_mobile.py, ui_mobile.py
#
#  Запуск на ПК для тестування:
#      python main_mobile.py
#  Для Android (Buildozer) — стандартний main файл.
# ─────────────────────────────────────────────
import sys, os
import pygame

from settings_mobile import (
    MOBILE_DEFAULT_W, MOBILE_DEFAULT_H, FPS, WINDOW_TITLE,
    TAB_HOME, TAB_CLICK, TAB_WORKERS,
    TAB_REBIRTH, TAB_ACHIEVEMENTS, TAB_STATS, TAB_SETTINGS,
    MUSIC_FILE,
)
from settings_mobile import COLOR_BG
from game      import GameState
from save_load import save, load, delete_save
import ui_mobile as ui

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# ══════════════════════════════════════════════
#  Iнiцiалiзацiя
# ══════════════════════════════════════════════
def init() -> tuple[pygame.Surface, pygame.time.Clock]:
    """Iнiцiалiзує pygame, вiкно, шрифти, зображення."""
    pygame.init()
    pygame.mixer.init()

    # На реальному Android-пристрої set_mode((0,0)) вiдкриє повний екран.
    # На ПК — використовуємо фiксований розмiр для тестування.
    try:
        info = pygame.display.Info()
        # перевiряємо чи є реальний пристрiй (розмiр вiдрiзняється вiд стандартного)
        if info.current_w > 0 and info.current_h > 0:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((MOBILE_DEFAULT_W, MOBILE_DEFAULT_H))
    except Exception:
        screen = pygame.display.set_mode((MOBILE_DEFAULT_W, MOBILE_DEFAULT_H))

    pygame.display.set_caption(WINDOW_TITLE)

    # передаємо реальний розмiр вiкна в ui_mobile
    w, h = screen.get_size()
    ui.set_screen_size(w, h)

    clock = pygame.time.Clock()
    ui.init_fonts()
    ui.init_images()
    return screen, clock


def start_music():
    """Запускає фонову музику якщо файл iснує."""
    try:
        pygame.mixer.music.load(resource_path(MUSIC_FILE))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


def load_sounds() -> dict:
    """Завантажує звуковi ефекти."""
    sounds = {}
    for name, path in [("click", "assets/sounds/click.wav"),
                        ("buy",   "assets/sounds/buy.wav")]:
        try:
            s = pygame.mixer.Sound(resource_path(path))
            s.set_volume(0.4)
            sounds[name] = s
        except Exception:
            sounds[name] = None
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
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.duration   = 0.0

    def move(self, x: int, y: int):
        self.cur_x = x
        self.cur_y = y
        self.duration = pygame.time.get_ticks() / 1000.0 - self.start_time

    def end(self) -> bool:
        """Повертає True якщо дотик можна вважати тапом."""
        dx = abs(self.cur_x - self.start_x)
        dy = abs(self.cur_y - self.start_y)
        dist = (dx * dx + dy * dy) ** 0.5
        self.active = False
        return dist <= self.TAP_MAX_DIST and self.duration <= self.TAP_MAX_TIME

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
def handle_events(game: GameState, sounds: dict,
                  current_tab: str,
                  screen: pygame.Surface) -> tuple[bool, str]:
    """
    Обробляє всi подiї pygame.
    Повертає (running, current_tab).
    running=False означає вихiд з гри.
    """
    global _slider_drag

    for event in pygame.event.get():

        # ── Закриття вiкна ────────────────────
        if event.type == pygame.QUIT:
            save(game)
            return False, current_tab

        # ── Клавiатура (для тестування на ПК) ─
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save(game)
            elif event.key == pygame.K_ESCAPE:
                save(game)
                return False, current_tab

        # ── Вiдпускання мишi / пальця (кiнець слайдера) ──
        if event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            _slider_drag = False

        # ─────────────────────────────────────────────────
        #  FINGER-подiї (реальний сенсорний екран)
        # ─────────────────────────────────────────────────
        if event.type == pygame.FINGERDOWN:
            fx, fy = finger_to_px(event, screen)
            _handle_touch_begin(fx, fy, current_tab)

        elif event.type == pygame.FINGERMOTION:
            fx, fy = finger_to_px(event, screen)
            current_tab = _handle_touch_move(fx, fy, current_tab, game, sounds)

        elif event.type == pygame.FINGERUP:
            fx, fy = finger_to_px(event, screen)
            result = _handle_touch_end(fx, fy, current_tab, game, sounds)
            if result is False:
                return False, current_tab
            if result is not None:
                current_tab = result

        # ─────────────────────────────────────────────────
        #  MOUSE-подiї (для тестування на ПК)
        # ─────────────────────────────────────────────────
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            _handle_touch_begin(mx, my, current_tab)

        elif event.type == pygame.MOUSEMOTION:
            if any(btn for btn in pygame.mouse.get_pressed()):
                mx, my = event.pos
                current_tab = _handle_touch_move(mx, my, current_tab, game, sounds)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mx, my = event.pos
            result = _handle_touch_end(mx, my, current_tab, game, sounds)
            if result is False:
                return False, current_tab
            if result is not None:
                current_tab = result

        # ── Скрол колесом мишi (для ПК) ──────
        elif event.type == pygame.MOUSEWHEEL:
            if current_tab in (TAB_CLICK, TAB_WORKERS):
                typ = "click" if current_tab == TAB_CLICK else "worker"
                ui.scroll_upgrades(typ, float(-event.y * 25))
                ui.clamp_upgrade_scroll(typ, game)

    return True, current_tab


def _handle_touch_begin(x: int, y: int, current_tab: str):
    """Обробляє початок дотику: визначає в якiй зонi."""
    global _slider_drag
    from ui_mobile import RES_BAR_H, TAB_BAR_H
    from settings_mobile import TAB_BAR_H as _tbh

    tab_bar_y = ui.H - ui.TAB_BAR_H

    if y < ui.RES_BAR_H:
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

    tab_bar_y = ui.H - ui.TAB_BAR_H

    if _slider_drag and current_tab == TAB_SETTINGS:
        # тягнемо слайдер
        vol = ui.slider_volume_at(x)
        if vol is not None:
            game.music_volume = vol
            try:
                pygame.mixer.music.set_volume(vol)
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
    tab_bar_y = ui.H - ui.TAB_BAR_H

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
def render(screen: pygame.Surface, game: GameState, current_tab: str, dt: float):
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

    pygame.display.flip()


# ══════════════════════════════════════════════
#  Головна функцiя
# ══════════════════════════════════════════════
def main():
    screen, clock = init()
    sounds = load_sounds()
    start_music()

    # завантаження збереження
    game = GameState()
    offline_earned = load(game)
    ui.show_offline_message(offline_earned, game.format_number)

    # застосовуємо збережену гучнiсть
    try:
        pygame.mixer.music.set_volume(game.music_volume)
    except Exception:
        pass

    current_tab = TAB_HOME
    running     = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)

        running, current_tab = handle_events(game, sounds, current_tab, screen)
        game.update(dt)
        maybe_autosave(game, dt)
        ui.tick_achievement_banner(game, dt)

        # оновлення частинок кiнцевої анiмацiї
        if game.end_anim_timer > 0 or game.show_end_dialog:
            ui.update_end_animation(dt)

        render(screen, game, current_tab, dt)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()