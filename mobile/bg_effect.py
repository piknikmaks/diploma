# ─────────────────────────────────────────────
#  bg_effect.py — анімований фон (рух + перелив)
# ─────────────────────────────────────────────
from __future__ import annotations

import math
import random

import pygame

from settings import (
    COLOR_BG,
    COLOR_BG_GLOW_ALPHA,
    BG_BLOB_COUNT,
    BG_BLOB_ALPHA,
    BG_SHIMMER_ALPHA,
    BG_PULSE_SPEED,
)

GLOW_COLORS = [
    (110, 100, 220),
    (220, 100, 100),
    (100, 200, 100),
    (220, 180, 50),
    (50, 200, 220),
    (220, 80, 220),
]


class _Blob:
    __slots__ = (
        "ox", "oy", "radius", "color",
        "phase", "speed", "drift", "pulse_phase", "pulse_speed",
    )

    def __init__(self, w: int, h: int, color: tuple[int, int, int]):
        span = min(w, h)
        self.ox = random.uniform(0.12, 0.88) * w
        self.oy = random.uniform(0.12, 0.88) * h
        self.radius = random.uniform(0.16, 0.34) * span
        self.color = color
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.22, 0.5)
        self.drift = random.uniform(0.1, 0.24) * span
        self.pulse_phase = random.uniform(0, math.tau)
        self.pulse_speed = random.uniform(0.7, 1.5)

    def pos(self, t: float) -> tuple[float, float]:
        x = self.ox + math.sin(t * self.speed + self.phase) * self.drift
        y = self.oy + math.cos(t * self.speed * 0.82 + self.phase * 1.25) * self.drift
        return x, y

    def current_radius(self, t: float) -> float:
        return self.radius * (1.0 + 0.14 * math.sin(t * self.pulse_speed + self.pulse_phase))


_blobs: list[_Blob] = []
_blob_area = (0, 0)


def reset_bg_effect():
    global _blobs, _blob_area
    _blobs = []
    _blob_area = (0, 0)


def _ensure_blobs(w: int, h: int):
    global _blobs, _blob_area
    if (w, h) == _blob_area and _blobs:
        return
    _blob_area = (w, h)
    _blobs = [_Blob(w, h, GLOW_COLORS[i % len(GLOW_COLORS)]) for i in range(BG_BLOB_COUNT)]


def _blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _draw_soft_circle(surface, cx, cy, radius, color, alpha_base: int):
    r = max(4, int(radius))
    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        alpha = int(alpha_base * (i / 6))
        pygame.draw.circle(s, (*color, alpha), (r, r), max(2, int(r * i / 6)))
    surface.blit(s, (int(cx) - r, int(cy) - r))


def draw_animated_bg(surface, rect: pygame.Rect, rebirth_count: int = 0):
    """Фон із рухомими плямами світла, переливами та пульсуючою підсвіткою."""
    x, y, w, h = rect.x, rect.y, rect.w, rect.h
    if w <= 0 or h <= 0:
        return

    surface.fill(COLOR_BG, rect)
    _ensure_blobs(w, h)

    t = pygame.time.get_ticks() / 1000.0
    accent = GLOW_COLORS[min(rebirth_count, len(GLOW_COLORS) - 1)]
    secondary = GLOW_COLORS[(min(rebirth_count, len(GLOW_COLORS) - 1) + 2) % len(GLOW_COLORS)]

    for blob in _blobs:
        bx, by = blob.pos(t)
        br = blob.current_radius(t)
        mix = 0.3 + 0.3 * math.sin(t * 0.65 + blob.phase)
        col = _blend(blob.color, accent, mix)
        _draw_soft_circle(surface, x + bx, y + by, br, col, BG_BLOB_ALPHA)

    shimmer_a = int(BG_SHIMMER_ALPHA * (0.5 + 0.5 * math.sin(t * BG_PULSE_SPEED)))
    shimmer_col = _blend(accent, secondary, 0.5 + 0.5 * math.sin(t * 0.85))
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((*shimmer_col, shimmer_a))
    surface.blit(overlay, (x, y))

    band_cy = y + h * (0.5 + 0.38 * math.sin(t * 0.32))
    _draw_soft_circle(surface, x + w // 2, band_cy, w * 0.55, accent, 7)

    cx, cy = x + w // 2, y + h // 2
    pulse = 1.0 + 0.2 * math.sin(t * BG_PULSE_SPEED * 1.15)
    max_r = max(8, int(min(w, h) // 2 * pulse))
    alpha_mult = 1.0 + 0.45 * math.sin(t * BG_PULSE_SPEED * 1.55)
    gsurf = pygame.Surface((max_r * 2, max_r * 2), pygame.SRCALPHA)
    for i in range(10, 0, -1):
        alpha = int(COLOR_BG_GLOW_ALPHA * alpha_mult * (i / 10))
        pygame.draw.circle(gsurf, (*accent, alpha), (max_r, max_r), max(2, int(max_r * i / 10)))
    surface.blit(gsurf, (cx - max_r, cy - max_r))
