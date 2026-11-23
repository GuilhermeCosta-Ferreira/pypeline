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
    """The `output` section: where results go and which step outputs are saved.

    Attributes:
        out_dir: Folder results are written to.
        fmts: Not used yet.
        save_all_intermediates: Not used yet.
        save_points: Step outputs to save. Allos for specific intermediate checkpoints

    Examples:
        output:
          out_dir: results
          fmts: {}
          save_all_intermediates: false
          save_points:
            - after: blur
              subdir: blurred
    """

    out_dir: Path
    fmts: FormatsMap
    save_all_intermediates: bool
    save_points: list[SavePoint] = field(default_factory=list)
