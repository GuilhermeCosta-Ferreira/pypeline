# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Protocol

from .actors import ActorRecord
from ..pipeline import SavePoint


# ================================================================
# 1. Section: Functions
# ================================================================
class Saver(Protocol):
    """Writes step outputs for save points."""

    def save(self, output: ActorRecord, point: SavePoint) -> None:
        """Write `output.object` where and how `point` says."""
