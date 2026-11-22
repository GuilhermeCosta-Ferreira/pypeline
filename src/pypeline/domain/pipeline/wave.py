# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass

from ..step import Step


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class Wave:
    single_steps: list[tuple[int, Step]]
    global_steps: list[tuple[int, Step]]


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Helper Functions
# ──────────────────────────────────────────────────────
def build_waves(steps: list[Step]) -> list[Wave]:
    waves: list[Wave] = []
    singles: list[tuple[int, Step]] = []
    globals_: list[tuple[int, Step]] = []

    for idx, step in enumerate(steps):
        # 1. A single step after globals closes the current wave
        if step.scope == "single" and globals_:
            waves.append(Wave(singles, globals_))
            singles, globals_ = [], []

        # 2. Adds the step to its side of the wave
        (globals_ if step.scope == "global" else singles).append((idx, step))

    if singles or globals_:
        waves.append(Wave(singles, globals_))
    return waves
