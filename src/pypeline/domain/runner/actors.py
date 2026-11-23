# ================================================================
# 0. Section: IMPORTS
# ================================================================
import polars as pl

from typing import Any
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
    """References to the actors currently in a run, never the actors themselves.

    Examples:
        One row per actor; inputs have `step_idx == INPUT_STEP`:

            path                      | step_idx | class_name
            "data/batch_1/img_01.png" |    -1    | "Image"
            "temp/stats_0.pkl"        |     2    | "ImageStats"
    """

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
    """Reference to one actor; `object` is set only while it is loaded, and `step_idx`
    is the step that produced it."""

    path: Path | None
    step_idx: int
    class_name: str

    object: Any | None = None
