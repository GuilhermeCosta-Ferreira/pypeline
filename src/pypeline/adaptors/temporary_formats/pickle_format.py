# ================================================================
# 0. Section: IMPORTS
# ================================================================
import pickle

from pathlib import Path
from typing import Any, ClassVar
from dataclasses import dataclass


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class PickleFormat:
    """`TempFileFormat` using pickle; every actor must be picklable."""

    extension: ClassVar[str] = ".pkl"

    def write(self, obj: Any, path: Path) -> None:
        with path.open("wb") as f:
            pickle.dump(obj, f)

    def read(self, path: Path) -> Any:
        with path.open("rb") as f:
            return pickle.load(f)
