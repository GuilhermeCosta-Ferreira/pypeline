# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Protocol

from pypeline.types import FilesMap

from .actors import ActorRecord
from ..pipeline.settings import InputSettings


# ================================================================
# 1. Section: Functions
# ================================================================
class Loader(Protocol):
    """Reads actors from disk, input files and temp files alike."""

    def load(self, actor: ActorRecord) -> ActorRecord:
        """Return `actor` with `object` set to the value read from `actor.path`."""
        ...

    def files(self, input_settings: InputSettings) -> FilesMap:
        """List every input file with the actor class its extension maps to.

        Returns:
            `(class name, path)` pairs, one per file.
        """
        ...
