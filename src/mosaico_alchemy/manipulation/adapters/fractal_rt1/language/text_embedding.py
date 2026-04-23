from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.text_embedding import TextEmbedding


class FractalRT1TextEmbeddingAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.text_embedding"
    ontology_type = TextEmbedding

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=TextEmbedding(values=payload.get("values", [])),
        )
