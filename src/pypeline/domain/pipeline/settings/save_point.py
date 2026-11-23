# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass, field

from pypeline.types import FormatsMap


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class SavePoint:
    """Save a step's output right after that step runs.

    Attributes:
        after: `name` of the step whose output is saved.
        occurrence: Which use of that step, counting from 1, when the pipeline uses it
            more than once.
        subdir: Folder inside `out_dir` to save into.
        fmts: Not used yet.

    Examples:
        With steps `blur`, `sharpen`, `blur`, this saves the output of the second
        `blur`:

            - after: blur
              occurrence: 2
    """

    after: str
    occurrence: int = 1
    subdir: Path | None = None
    fmts: FormatsMap = field(default_factory=dict)
