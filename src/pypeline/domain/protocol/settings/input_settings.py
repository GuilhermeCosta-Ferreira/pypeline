# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class InputSettings:
    data_dirs: list[Path]
    data_fmts: list[str]
