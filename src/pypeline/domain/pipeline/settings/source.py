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
        depth: How many folder levels to read, counting `path` itself as 1. `None`
            reads every subfolder.
        include_hidden_folders: Also read folders whose name starts with `.`.
        include_hidden_files: Also read files whose name starts with `.`.
    """

    path: Path
    load_as: FormatsMap = field(default_factory=dict)
    depth: int | None = 1
    include_hidden_folders: bool = False
    include_hidden_files: bool = False
