# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class GlobalSettings:
    protocol_name: str
    check_scope: bool
