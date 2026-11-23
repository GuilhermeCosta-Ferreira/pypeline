# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from typing import Protocol, Any, ClassVar



# ================================================================
# 1. Section: Functions
# ================================================================
class TempFileFormat(Protocol):
    extension: ClassVar[str]

    def write(self, obj: Any, path: Path) -> None: ...

    def read(self, path: Path) -> Any: ...
