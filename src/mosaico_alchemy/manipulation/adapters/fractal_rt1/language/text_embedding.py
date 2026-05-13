from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.text_embedding import TextEmbedding


class FractalRT1TextEmbeddingAdapter(BaseAdapter[TextEmbedding]):
    """
    Adapter for text embedding data in FractalRT1 datasets.

    Translates text embedding data from the dataset's message format to the
    `TextEmbedding` ontology type.
    """

    adapter_id = "fractal_rt1.text_embedding"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "values")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=TextEmbedding(values=payload["values"]),
        )
