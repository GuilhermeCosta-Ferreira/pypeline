# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from collections.abc import Callable
from typing import Any, ClassVar, final



# ================================================================
# 1. Section: Functions
# ================================================================
class ActorLoader:
    formats: ClassVar[dict[str, Callable[[Path], Any]]] # the user maps loader functions to each suffix

    @final
    def load(self, path: Path) -> Any:
        if path.suffix not in self.formats:
            raise ValueError(
                f"{type(self).__name__} cannot read {path.suffix!r}. "
                f"Supported: {sorted(self.formats)}"
            )
        return self.formats[path.suffix](path)
