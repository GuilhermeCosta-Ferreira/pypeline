# ================================================================
# 0. Section: IMPORTS
# ================================================================
import tomllib

from pathlib import Path
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable

BUILTIN_TEMPLATES: Traversable = files("pypeline") / "templates"


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class PipelineTemplates:
    """Templates for new pipeline files: the built-in ones plus those in `folder`.

    A template is a `.yaml` file whose name, without the extension, is the template's
    name. A template in `folder` wins over a built-in one with the same name. The only
    built-in template is `default`.

    Attributes:
        folder: Folder holding your own templates. If `None`, only the built-in
            templates are available.

    Examples:
        >>> PipelineTemplates().create(Path("pipeline.yaml"))

        From one of your own templates:

        >>> templates = PipelineTemplates(Path("my_project/templates"))
        >>> templates.create(Path("runs/denoise.yaml"), "denoise")

        Using the folder set in your `pyproject.toml`, like the `pypeline` command:

        >>> PipelineTemplates.from_pyproject().create(Path("runs/denoise.yaml"), "denoise")
    """

    folder: Path | None = None

    @classmethod
    def from_pyproject(cls, start: Path | None = None) -> PipelineTemplates:
        """Use the templates folder set in the nearest `pyproject.toml`.

        Looks in `start` (the current folder by default) and then in each parent folder
        for a `pyproject.toml`, and reads `templates` from its `[tool.pypeline]` table.
        A relative path is resolved against the folder of that `pyproject.toml`. Only
        the nearest `pyproject.toml` is read; without the setting, only the built-in
        templates are available.

        Examples:
            With this in your project's `pyproject.toml`:

                [tool.pypeline]
                templates = "my_project/templates"

            >>> PipelineTemplates.from_pyproject().folder
            PosixPath('/home/me/my_project/my_project/templates')
        """
        start = (start or Path.cwd()).resolve()
        for folder in [start, *start.parents]:
            pyproject = folder / "pyproject.toml"
            if pyproject.is_file():
                with pyproject.open("rb") as f:
                    setting = tomllib.load(f).get("tool", {}).get("pypeline", {})
                if "templates" not in setting:
                    return cls()
                return cls(folder / setting["templates"])
        return cls()

    def names(self) -> list[str]:
        """Return the names of every available template.

        Raises:
            FileNotFoundError: If `folder` is not an existing folder.

        Examples:
            >>> PipelineTemplates(Path("my_project/templates")).names()
            ['default', 'denoise']
        """
        return sorted(self._templates())

    def create(
        self, path: Path, template: str = "default", overwrite: bool = False
    ) -> Path:
        """Write a new pipeline file at `path`, copied from a template.

        Args:
            path: Where to write the new pipeline file. Missing parent folders are
                created.
            template: Name of the template to copy.
            overwrite: Replace `path` if it already exists.

        Returns:
            `path`, so the call can feed straight into `Pypeline`.

        Raises:
            ValueError: If no template is named `template`.
            FileExistsError: If `path` exists and `overwrite` is False.
            FileNotFoundError: If `folder` is not an existing folder.
        """
        # 1. Finds the template before touching the target
        source = self._template_file(template)
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists")

        # 2. Copies it
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source.read_text())
        return path

    # ──────────────────────────────────────────────────────
    # 1.1 Subsection: Helper Functions
    # ──────────────────────────────────────────────────────
    def _templates(self) -> dict[str, Traversable]:
        # Later folders win, so the user's folder overrides the built-ins
        found: dict[str, Traversable] = {}
        folders: list[Traversable] = [BUILTIN_TEMPLATES]
        if self.folder is not None:
            folders.append(self.folder)
        for folder in folders:
            for entry in folder.iterdir():
                if entry.is_file() and entry.name.endswith(".yaml"):
                    found[entry.name.removesuffix(".yaml")] = entry
        return found

    def _template_file(self, name: str) -> Traversable:
        found = self._templates()
        if name not in found:
            raise ValueError(f"Unknown template {name!r}. Available: {sorted(found)}")
        return found[name]
