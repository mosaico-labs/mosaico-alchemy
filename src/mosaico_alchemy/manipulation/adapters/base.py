"""
Base contract for payload-to-ontology adapters.

Adapters isolate dataset-specific payload shapes from the ontology models expected
by the ingestion pipeline. This keeps discovery code focused on locating data while
the translation logic lives in small, composable classes.
"""

from abc import ABC, abstractmethod
from typing import Generic, Sized, Type, TypeVar

from mosaicolabs import Serializable

T = TypeVar("T", bound=Serializable)


class BaseAdapter(ABC, Generic[T]):
    """
    Abstract base class for translating raw payload dictionaries into ontology objects.

    Concrete adapters are intentionally lightweight: they declare a stable
    `adapter_id` used by descriptors and a target `__msco_ontology_type__` used by the
    runner when creating topics. The actual conversion happens in :meth:`translate`.
    """

    adapter_id: str
    __msco_ontology_type__: Type[T]
    _REQUIRED_KEYS: tuple[str, ...] = ()
    _AT_LEAST_ONE: tuple[str, ...] = ()

    @classmethod
    @abstractmethod
    def translate(cls, payload: dict):
        """
        Converts one raw dataset payload into the ontology message written to Mosaico.

        Implementations should be pure translations: they should not perform I/O,
        mutate global state, or depend on hidden runner context. That makes adapters
        easy to test and safe to reuse across ingestion backends.

        Args:
            payload: Raw record produced by a dataset-specific iterator or reader.

        Returns:
            The ontology message instance that should be written for this payload.
        """
        raise NotImplementedError("Subclasses must implement the translate method.")

    @classmethod
    def _validate_payload(
        cls,
        payload: dict,
        *,
        constraints: dict[str, dict] | None = None,
    ):
        missing = [field for field in cls._REQUIRED_KEYS if payload.get(field) is None]

        if missing:
            raise ValueError(
                f"'{cls.adapter_id}' payload missing required fields: {', '.join(missing)}"
            )

        if cls._AT_LEAST_ONE:
            if all(payload.get(field) is None for field in cls._AT_LEAST_ONE):
                raise ValueError(
                    f"'{cls.adapter_id}' payload requires at least one of: {', '.join(cls._AT_LEAST_ONE)}"
                )

        # Length validation
        if constraints:
            for field, rules in constraints.items():
                value = payload.get(field)

                if value is None:
                    continue

                # exact length
                expected_len = rules.get("len")
                if expected_len is not None:
                    if not isinstance(value, Sized):
                        raise ValueError(
                            f"{cls.adapter_id} field '{field}' is not sized"
                        )

                    if len(value) != expected_len:
                        raise ValueError(
                            f"{cls.adapter_id} field '{field}' "
                            f"has length {len(value)} "
                            f"(expected {expected_len})"
                        )

                # non-empty
                if rules.get("not_empty"):
                    if not isinstance(value, Sized):
                        raise ValueError(
                            f"{cls.adapter_id} field '{field}' is not sized"
                        )

                    if len(value) == 0:
                        raise ValueError(
                            f"{cls.adapter_id} field '{field}' must not be empty"
                        )

                # exact type
                expected_type = rules.get("type")
                if expected_type is not None:
                    if not isinstance(value, expected_type):
                        raise ValueError(
                            f"{cls.adapter_id} field '{field}' "
                            f"has type {type(value)} "
                            f"(expected {expected_type})"
                        )
