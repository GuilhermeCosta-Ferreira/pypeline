# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from typing import Protocol

from .actors import ActorRecord


# ================================================================
# 1. Section: Functions
# ================================================================
class TempStorage(Protocol):
    def put(self, actor: ActorRecord) -> Path: ...
    def clear(self) -> None: ...
