"""
Base contract for payload-to-ontology adapters.

Adapters isolate dataset-specific payload shapes from the ontology models expected
by the ingestion pipeline. This keeps discovery code focused on locating data while
the translation logic lives in small, composable classes.
"""

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """
    Abstract base class for translating raw payload dictionaries into ontology objects.

    Concrete adapters are intentionally lightweight: they declare a stable
    `adapter_id` used by descriptors and a target `ontology_type` used by the
    runner when creating topics. The actual conversion happens in :meth:`translate`.
    """

    adapter_id: str
    ontology_type: type

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
