# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass, field

FormatsMap = dict[str, str]


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class SavePoint:
    after: str
    occurrence: int = 1
    subdir: Path | None = None
    fmts: FormatsMap = field(default_factory=dict)
