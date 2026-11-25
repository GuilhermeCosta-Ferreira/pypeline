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
    """One pipeline file, checked on creation and ready to run.

    Creating it imports `packages`, so their steps and `ActorIO`s get registered, then
    reads the pipeline file and checks that every section, step and save point is
    valid, so mistakes surface before any data is processed.

    Attributes:
        path: Pipeline YAML file to read.
        packages: Names of the modules that register your steps and `ActorIO`s, as you
            would write them in an `import`. A package also has every module inside it
            imported, so new steps are picked up without editing an `__init__.py`.
            Name the package that holds them, not your whole project, or scripts in it
            get imported (and run) too.
        temp_fmt: Format for the intermediate files written between steps.
        temp_root: Folder in which each run creates its own temporary folder; the
            system temp folder if `None`. Point it at a disk with enough space when
            intermediates are large. Only the per-run folder is deleted, never
            `temp_root` itself.
        pipeline: The validated pipeline built from `path`.

    Raises:
        ModuleNotFoundError: If a name in `packages` cannot be imported.
        FileNotFoundError: If `path` does not exist.
        PipelineError: If the file is not a mapping of sections, or a section, step or
            save point is invalid, or the steps cannot run in the given order.

    Examples:
        >>> pypeline = Pypeline(Path("denoise.yaml"), packages=["my_project.steps"])
        >>> pypeline.run()

        Keeping intermediates on a scratch disk:

        >>> Pypeline(
        ...     Path("denoise.yaml"),
        ...     packages=["my_project.steps"],
        ...     temp_root=Path("/scratch"),
        ... ).run()
    """

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
        """Run every step on the input files and write the outputs the save points ask
        for.

        Intermediate files are deleted when the run ends, including when it fails.
        Errors raised inside a step are not caught.

        Raises:
            RunnerError: If a global step finds no actor of its input class.
            ValueError: If an actor class has no registered `ActorIO`, its `ActorIO`
                cannot read or write a needed extension, or a saved class has no output
                format.
        """
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
