# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from dataclasses import dataclass

from .saver import Saver
from .loader import Loader
from .protocol import Protocol
from .temp_storage import TempStorage



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Runner:
    loader: Loader
    saver: Saver
    temp_storage: TempStorage

    def run(self, protocol: Protocol) -> Any:
        pass
