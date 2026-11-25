# ================================================================
# 0. Section: IMPORTS
# ================================================================
import pkgutil
import tempfile
import importlib

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

    packages: list[str] = field(default_factory=list)
    temp_fmt: TempFileFormat = field(default_factory=PickleFormat)
    temp_root: Path | None = None
    pipeline: Pipeline = field(init=False)

    def __post_init__(self) -> None:
        import_packages(self.packages)
        draft = PipelineLoader().read(self.path)
        self.pipeline = PipelineBuilder().build(draft)

    def run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pypeline_", dir=self.temp_root) as tmp:
            runner = Runner(
                loader=FileLoader(temp_fmt=self.temp_fmt),
                saver=FileSaver(
                    self.pipeline.output_settings.out_dir,
                    self.pipeline.output_settings.fmts,
                ),
                temp_storage=FileTempStorage(root=Path(tmp), fmt=self.temp_fmt),
            )
            runner.run(self.pipeline)


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Helper Functions
# ──────────────────────────────────────────────────────
def import_packages(names: list[str]) -> None:
    """Import each module in `names`; for a package, also every module under it."""
    for name in names:
        module = importlib.import_module(name)
        if hasattr(module, "__path__"):
            for info in pkgutil.walk_packages(module.__path__, prefix=f"{name}."):
                importlib.import_module(info.name)
