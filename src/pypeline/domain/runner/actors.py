# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any

import polars as pl

from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterator

from pypeline.types import FilesMap

INPUT_STEP: int = -1
SCHEMA: pl.Schema = pl.Schema(
    {
        "path": pl.String,
        "step_idx": pl.Int32,
        "class_name": pl.String,
    }
)


# ================================================================
# 1. Section: Class and Inits
# ================================================================
class Actors:
    def __init__(self) -> None:
        self.table = pl.DataFrame(schema=SCHEMA)

    def __iter__(self) -> Iterator[ActorRecord]:
        for row in self.table.iter_rows(named=True):
            yield ActorRecord(Path(row["path"]), row["step_idx"], row["class_name"])

    @classmethod
    def from_files(cls, files: FilesMap) -> Actors:
        actors = cls()
        actors.table = pl.DataFrame(
            [(str(path), INPUT_STEP, actor) for actor, path in files],
            schema=SCHEMA,
            orient="row",
        )
        return actors

    @classmethod
    def from_records(cls, records: list[ActorRecord]) -> Actors:
        actors = cls()
        actors.table = pl.DataFrame(
            [(str(r.path), r.step_idx, r.class_name) for r in records],
            schema=SCHEMA,
            orient="row",
        )
        return actors



# ================================================================
# 2. Section: Unit Class
# ================================================================
@dataclass(frozen=True)
class ActorRecord:
    path: Path | None
    step_idx: int
    class_name: str

    object: Any | None = None


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
