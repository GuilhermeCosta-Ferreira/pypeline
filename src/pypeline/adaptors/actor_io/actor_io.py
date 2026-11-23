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
    """How one actor class is read from and written to files, one function per extension.

    Subclass it once per actor class and register the subclass in `ActorIORegistry`
    under the class name the pipeline file uses. Fill only the side you need: an actor
    that is never saved needs no `writers`. The actor class itself is never touched, so
    this works for classes you do not own.

    Attributes:
        readers: Extension to a function that reads a file into an actor.
        writers: Extension to a function that writes an actor to a file.

    Examples:
        >>> @ActorIORegistry.register("Image")
        ... class ImageIO(ActorIO):
        ...     @staticmethod
        ...     def read_png(path: Path) -> Image: ...
        ...
        ...     readers = {".png": read_png}
    """

    readers: ClassVar[dict[str, Callable[[Path], Any]]] = {}
    writers: ClassVar[dict[str, Callable[[Any, Path], None]]] = {}

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
