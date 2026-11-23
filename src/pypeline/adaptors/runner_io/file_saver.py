# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import dataclass, field

from pypeline.types import FormatsMap

from ...domain.runner import ActorRecord
from ...domain.pipeline import SavePoint
from ..actor_io import ActorIORegistry


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class FileSaver:
    """`Saver` that writes through `ActorIORegistry`, one file per output format.

    Files are named `{class name}_{n}{extension}` with one counter for the whole run,
    so outputs never overwrite each other.

    Attributes:
        out_dir: Folder save points write into, under their `subdir` if set.
        fmts: Output formats used when a save point sets none for the class.
    """

    out_dir: Path
    fmts: FormatsMap
    _count: int = field(default=0, init=False)

    def save(self, output: ActorRecord, point: SavePoint) -> None:
        """Write `output.object` once per output format of its class.

        Raises:
            ValueError: If neither `point.fmts` nor `fmts` has a format for the class.
        """
        # 1. The save point's formats win over the output section's
        exts = extensions(point.fmts, output.class_name) or extensions(
            self.fmts, output.class_name
        )
        if not exts:
            raise ValueError(f"No output format for {output.class_name}")

        # 2. Writes one file per format, all sharing a name
        folder = self.out_dir / point.subdir if point.subdir else self.out_dir
        folder.mkdir(parents=True, exist_ok=True)
        io = ActorIORegistry.get(output.class_name)
        for ext in exts:
            io.save(output.object, folder / f"{output.class_name}_{self._count}{ext}")
        self._count += 1


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Helper Functions
# ──────────────────────────────────────────────────────
def extensions(fmts: FormatsMap, class_name: str) -> list[str]:
    return [ext for ext, name in fmts.items() if name == class_name]
