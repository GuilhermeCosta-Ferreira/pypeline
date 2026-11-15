# ================================================================
# 0. Section: IMPORTS
# ================================================================
import typing

from typing import Any



# ================================================================
# 1. Section: Functions
# ================================================================
class TempStorage(typing.Protocol):
    def put(self, key: str, data: Any) -> None: ...

    def get(self, key: str) -> Any: ...

    def clear(self) -> None: ...
