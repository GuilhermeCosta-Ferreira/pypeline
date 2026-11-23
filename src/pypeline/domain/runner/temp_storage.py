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
    """Holds actors between the phases of a run."""

    def put(self, actor: ActorRecord) -> Path:
        """Write `actor.object` and return a path the `Loader` can read it back from."""
        ...

    def clear(self) -> None:
        """Delete everything `put` wrote during the run."""
