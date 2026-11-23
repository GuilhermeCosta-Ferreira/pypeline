# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from collections.abc import Callable
from typing import ClassVar, Any, final


# ================================================================
# 1. Section: Functions
# ================================================================
class ActorIO:
    readers: ClassVar[dict[str, Callable[[Path], Any]]] = {}
    writers: ClassVar[dict[str, Callable[[Any, Path], None]]] = {}

    @final
    def load(self, path: Path) -> Any:
        if path.suffix not in self.readers:
            raise ValueError(
                f"{type(self).__name__} cannot read {path.suffix!r}. "
                f"Supported: {sorted(self.readers)}"
            )
        return self.readers[path.suffix](path)

    @final
    def save(self, obj: Any, path: Path) -> None:
        if path.suffix not in self.writers:
            raise ValueError(
                f"{type(self).__name__} cannot write {path.suffix!r}. "
                f"Supported: {sorted(self.writers)}"
            )
        self.writers[path.suffix](obj, path)
