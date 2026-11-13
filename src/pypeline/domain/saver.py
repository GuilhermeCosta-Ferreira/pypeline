# ================================================================
# 0. Section: IMPORTS
# ================================================================
import typing

from dataclasses import dataclass

from .protocol import SavePoint



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Saver(typing.Protocol):
    def save(self, data: object, point: SavePoint) -> None: ...
