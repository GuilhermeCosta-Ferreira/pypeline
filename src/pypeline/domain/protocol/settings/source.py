# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass,field

FormatsMap = dict[str, str]



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class Source:
    path: Path
    load_as: FormatsMap = field(default_factory=dict)
