from mosaicolabs import Message, Vector2d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1Vector2dAdapter(BaseAdapter[Vector2d]):
    """
    Adapter for vector2d data in FractalRT1 datasets.

    Translates vector2d data from the dataset's message format to the
    `mosaicolabs.Vector2d` ontology type.
    """

    adapter_id = "fractal_rt1.vector2d"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "vector")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        cls._validate_payload(payload=payload, constraints={"vector": {"len": 2}})
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Vector2d.from_list(payload["vector"]),
        )
