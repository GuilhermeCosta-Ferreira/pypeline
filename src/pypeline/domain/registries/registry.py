# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import ClassVar
from collections.abc import Callable


# ================================================================
# 1. Section: Class definition
# ================================================================
class Registry[T]:
    """Map string keys to classes so they can be looked up and built by name.

    When playing with interfaces and abstract classes, registry becomes the tool of
    choice to make sure we can call either implemented class through a "tag".

    Examples:
        >>> class DecoderRegistry(Registry[Decoder]):
        ...     pass
        >>> @DecoderRegistry.register("lda")
        ... class LDADecoder(Decoder):
        ...     ...
        >>> decoder = DecoderRegistry.get("lda")
    """

    # A. All the registration entities live here
    _entries: ClassVar[dict[str, type]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls._entries = {}

    @classmethod
    def register(cls, key: str) -> Callable[[type[T]], type[T]]:
        """Class decorator that adds the decorated class to this registry under `key`.

        Raises:
            ValueError: If `key` is already registered in this registry.
        """

        def decorator(target_cls: type[T]) -> type[T]:
            # 1. Make sure there is a new key
            if key in cls._entries:
                raise ValueError(f"Key {key!r} already registered in {cls.__name__}")

            # 2. Adds the key-class pair to the registry
            cls._entries[key] = target_cls
            return target_cls

        return decorator

    @classmethod
    def get(cls, key: str) -> T:
        """Create a new instance of the class registered under `key`.

        The class is called with no arguments. For classes that need constructor
        arguments, use `get_type` and instantiate the class yourself.
        """
        return cls.get_type(key)()

    @classmethod
    def get_type(cls, key: str) -> type[T]:
        """Return the class registered under `key`, without instantiating it.

        Raises:
            ValueError: If no class is registered under `key`.
        """
        if key not in cls._entries:
            raise ValueError(
                f"Unknown key {key!r} in {cls.__name__}. "
                f"Registered: {sorted(cls._entries)}"
            )
        return cls._entries[key]

    @classmethod
    def known_keys(cls) -> set[str]:
        """Returns all of the known registered keys."""
        return set(cls._entries)

    @classmethod
    def key_of(cls, target: T | type[T]) -> str:
        """Return the key `target` was registered under; the reverse of `get_type`.

        Args:
            target: A registered class or an instance of one. Only an exact match
                counts: a subclass of a registered class is not found unless it was
                registered itself.

        Raises:
            ValueError: If the class of `target` is not registered in this registry.
        """
        # 1. Deals with type vs instance
        target_cls = target if isinstance(target, type) else type(target)

        # 2. Loops to find it (if exists)
        for key, registered in cls._entries.items():
            if registered is target_cls:
                return key

        raise ValueError(f"{target_cls.__name__} is not registered in {cls.__name__}")
