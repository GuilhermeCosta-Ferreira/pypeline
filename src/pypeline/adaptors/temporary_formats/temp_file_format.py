# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from typing import Protocol, Any, ClassVar


# ================================================================
# 1. Section: Functions
# ================================================================
class TempFileFormat(Protocol):
    """Serialiser for temp files; `read` must return what `write` was given.

    Attributes:
        extension: Suffix of the files it writes, dot included.
    """

    extension: ClassVar[str]

    def write(self, obj: Any, path: Path) -> None: ...

    def read(self, path: Path) -> Any: ...
