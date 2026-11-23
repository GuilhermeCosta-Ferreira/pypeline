# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass, field

from ..adaptors import (
    TempFileFormat,
    PickleFormat,
    FileLoader,
    FileSaver,
    FileTempStorage,
    PipelineLoader,
)
from ..domain import Runner, Pipeline, PipelineBuilder


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Pypeline:
    path: Path

    temp_fmt: TempFileFormat = field(default_factory=PickleFormat)
    temp_root: Path | None = None
    pipeline: Pipeline = field(init=False)

    def __post_init__(self) -> None:
        draft = PipelineLoader().read(self.path)
        self.pipeline = PipelineBuilder().build(draft)

    def run(self) -> None:
        runner = Runner(
            loader=FileLoader(temp_fmt=self.temp_fmt),
            saver=FileSaver(
                self.pipeline.output_settings.out_dir,
                self.pipeline.output_settings.fmts,
            ),
            temp_storage=FileTempStorage(root=..., fmt=self.temp_fmt),
        )
        runner.run(self.pipeline)
