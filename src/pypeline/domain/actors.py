# ================================================================
# 0. Section: IMPORTS
# ================================================================
import polars as pl

from pathlib import Path

from pypeline.types import FilesMap

INPUT_STEP: int = -1
SCHEMA: pl.Schema = pl.Schema(
    {
        "path": pl.String,
        "step_idx": pl.UInt32,
        "class_name": pl.String,
    }
)


# ================================================================
# 1. Section: Class and Inits
# ================================================================
class Actors:
    def __init__(self) -> None:
        self.table = pl.DataFrame(schema=SCHEMA)

    @classmethod
    def from_files(cls, files: FilesMap) -> Actors:
        actors = cls()
        actors.table = pl.DataFrame(
            [(str(path), INPUT_STEP, actor) for actor, path in files],
            schema=SCHEMA,
            orient="row",
        )
        return actors



    # ================================================================
    # 2. Section: Methods
    # ================================================================
    def add(self, step_idx: int, entries: list[tuple[str, Path]]) -> None:
        rows = pl.DataFrame(
            [(str(path), step_idx, name) for name, path in entries],
            schema=SCHEMA,
            orient="row",
        )
        self._table = pl.concat([self._table, rows])




"""
data:
                   Path                    | Step Idx | Class Name

    "data/source_1/mouse_1.csv"            |    0     | "Syllable"
    "temp/source_1/mouse_1_dist01.csv"     |    3     | "Dist"
    "temp/source_1/mouse_1_syllable01.csv" |    3     | "Syllable"
    "data/source_1/mouse_2.csv"            |    3     | "Syllable"
    "temp/source_1/mouse_2_dist01.csv"     |    3     | "Dist"
    "temp/source_1/mouse_2_syllable01.csv" |    3     | "Syllable"
"""
