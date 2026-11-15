# ================================================================
# 0. Section: IMPORTS
# ================================================================
import typing

from typing import Any
from pathlib import Path
from dataclasses import dataclass

from pypeline.types import FormatsMap



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Loader(typing.Protocol):
    def load(self, path: Path, load_as: FormatsMap) -> dict[str, Any]: ...
