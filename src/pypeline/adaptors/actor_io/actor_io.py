# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from typing import ClassVar, Any, final

from pypeline.types import Reader, Writer


# ================================================================
# 1. Section: Functions
# ================================================================
class ActorIO:
    """How one actor class is read from and written to files, one function per extension.

    Usually built by `ActorIORegistry.add`, which shows how to register one.

    Attributes:
        readers: Extension to a function that reads a file into an actor.
        writers: Extension to a function that writes an actor to a file.
    """

    readers: ClassVar[dict[str, Reader]] = {}
    writers: ClassVar[dict[str, Writer]] = {}

    @final
    def load(self, path: Path) -> Any:
        """Read `path` with the reader for its extension.

        Raises:
            ValueError: If no reader is set for the extension.
        """
        if path.suffix not in self.readers:
            raise ValueError(
                f"{type(self).__name__} cannot read {path.suffix!r}. "
                f"Supported: {sorted(self.readers)}"
            )
        return self.readers[path.suffix](path)

    @final
    def save(self, obj: Any, path: Path) -> None:
        """Write `obj` to `path` with the writer for its extension.

        Raises:
            ValueError: If no writer is set for the extension.
        """
        if path.suffix not in self.writers:
            raise ValueError(
                f"{type(self).__name__} cannot write {path.suffix!r}. "
                f"Supported: {sorted(self.writers)}"
            )
        self.writers[path.suffix](obj, path)
