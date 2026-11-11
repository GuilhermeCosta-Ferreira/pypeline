# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass

from .source import Source, FormatsMap



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class InputSettings:
    load_as: FormatsMap
    sources: list[Source]
