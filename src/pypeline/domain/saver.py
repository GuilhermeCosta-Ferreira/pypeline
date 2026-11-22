# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Protocol
from dataclasses import dataclass

from .actors import ActorRecord
from .pipeline import SavePoint


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Saver(Protocol):
    def save(self, output: ActorRecord, point: SavePoint) -> None: ...
