# ================================================================
# 0. Section: IMPORTS
# ================================================================
import sys
import argparse

from pathlib import Path

from .service import PipelineTemplates


# ================================================================
# 1. Section: Functions
# ================================================================
def main(argv: list[str] | None = None) -> int:
    """Entry point of the `pypeline` command; returns the exit code."""
    args = _parser().parse_args(argv)

    # 1. `--templates` wins over the `[tool.pypeline]` setting
    templates = (
        PipelineTemplates(args.templates)
        if args.templates
        else PipelineTemplates.from_pyproject()
    )

    # 2. Runs the subcommand, turning expected failures into a message
    try:
        if args.command == "init":
            path = templates.create(args.path, args.template, args.force)
            print(f"Created {path} from template {args.template!r}")
        else:
            print("\n".join(templates.names()))
    except FileExistsError as error:
        print(f"pypeline: {error} (use --force to replace it)", file=sys.stderr)
        return 1
    except (ValueError, FileNotFoundError) as error:
        print(f"pypeline: {error}", file=sys.stderr)
        return 1
    return 0


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Helper Functions
# ──────────────────────────────────────────────────────
def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pypeline")
    commands = parser.add_subparsers(dest="command", required=True)

    # 1. Shared option: where the user's own templates live
    folder = argparse.ArgumentParser(add_help=False)
    folder.add_argument(
        "--templates",
        type=Path,
        help="folder with your templates (default: [tool.pypeline] templates "
        "in the nearest pyproject.toml)",
    )

    # 2. `init`: writes a new pipeline file
    init = commands.add_parser(
        "init", parents=[folder], help="create a pipeline file from a template"
    )
    init.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("pipeline.yaml"),
        help="file to create",
    )
    init.add_argument("--template", default="default", help="template name")
    init.add_argument("--force", action="store_true", help="overwrite an existing file")

    # 3. `templates`: lists the available names
    commands.add_parser("templates", parents=[folder], help="list available templates")
    return parser


if __name__ == "__main__":
    sys.exit(main())
