# Contributing

When contributing to this repository, please first discuss the change you wish to make via issues.

## Pull Request Process

1. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
2. Using AI in the process is fine, but the PR still needs to hold to the same standard.

## Code Quality

### Setup

```bash
poetry install
```

### Before opening a PR

```bash
make dev
```

This formats the code, then runs pylint, pyright and the tests. Everything must pass. Individual steps are available as `make format`, `make lint`, `make diagram` and `make test`.

### Type Annotations

- Type-hint all code; `pyright` must report no errors.
- For generic classes, use the Python 3.12+ syntax: `class Registry[T]:` instead of `TypeVar` + `Generic[T]`.
- Avoid `cast` unless pyright actually complains without it; it hides mistakes.

### Docstrings

- Write one only when it says something the name and type hints don't: an assumption, a unit, a side effect, an error the caller should expect, or the contract a subclass must follow.
- Use Google style (`Args:`, `Returns:`, `Raises:`, `Examples:`), and only the sections that add information.
- Write examples as doctests (`>>>`), so they render in Sphinx and run as tests.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 1.4, available at [http://contributor-covenant.org/version/1/4][version]

[homepage]: http://contributor-covenant.org
[version]: http://contributor-covenant.org/version/1/4/
