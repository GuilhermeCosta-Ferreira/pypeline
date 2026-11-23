# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from pathlib import Path

# ================================================================
# 1. Section: Types
# ================================================================
FormatsMap = dict[str, str]
FilesMap = list[tuple[str, Path]]
ActorState = tuple[str, Any | None]
