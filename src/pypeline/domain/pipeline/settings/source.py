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
class Source:
    """One input folder.

    Attributes:
        path: Folder to read files from; never a single file.
        load_as: Extra extension to actor class mappings for this folder only.
    """

    path: Path
    load_as: FormatsMap = field(default_factory=dict)
