# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass, field

from .save_point import SavePoint, FormatsMap


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class OutputSettings:
    out_dir: Path
    fmts: FormatsMap
    save_all_intermediates: bool
    save_points: list[SavePoint] = field(default_factory=list)
