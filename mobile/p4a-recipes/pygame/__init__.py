"""
Локальний рецепт pygame для python-for-android (pygame 2.5.x на Android).

https://github.com/pygame/pygame/issues/4394
"""
import os
from os.path import join

from pythonforandroid.recipes.pygame import Pygame2Recipe
from pythonforandroid.toolchain import current_directory

_SURFACE_OLD = (
    "surface src_c/surface.c src_c/alphablit.c src_c/surface_fill.c $(SDL) $(DEBUG)"
)
_SURFACE_NEW = (
    "surface src_c/simd_blitters_sse2.c src_c/simd_blitters_avx2.c "
    "src_c/surface.c src_c/alphablit.c src_c/surface_fill.c $(SDL) $(DEBUG)"
)


class Pygame2RecipeAndroidFix(Pygame2Recipe):
    def prebuild_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        template = join(build_dir, "buildconfig", "Setup.Android.SDL2.in")
        if os.path.isfile(template):
            with open(template, encoding="utf-8") as f:
                text = f.read()
            if _SURFACE_OLD in text:
                with open(template, "w", encoding="utf-8") as f:
                    f.write(text.replace(_SURFACE_OLD, _SURFACE_NEW, 1))
        super().prebuild_arch(arch)
        with current_directory(build_dir):
            setup_path = join(build_dir, "Setup")
            with open(setup_path, encoding="utf-8") as f:
                setup = f.read()
            if _SURFACE_OLD in setup:
                with open(setup_path, "w", encoding="utf-8") as f:
                    f.write(setup.replace(_SURFACE_OLD, _SURFACE_NEW, 1))
                print("[pygame recipe] patched Setup: surface simd blitters")


recipe = Pygame2RecipeAndroidFix()
