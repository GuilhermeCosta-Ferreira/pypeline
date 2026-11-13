# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from dataclasses import dataclass

from .saver import Saver
from .protocol import Protocol



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Runner:
    saver: Saver

    def run(self, data: Any, protocol: Protocol) -> Any:
        pass
