from mosaicolabs import Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1Vector3dAdapter(BaseAdapter[Vector3d]):
    """
    Adapter for vector3d data in FractalRT1 datasets.

    Translates vector3d data from the dataset's message format to the
    `mosaicolabs.Vector3d` ontology type.
    """

    adapter_id = "fractal_rt1.vector3d"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "vector")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        cls._validate_payload(payload=payload, constraints={"vector": {"len": 3}})
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Vector3d.from_list(payload["vector"]),
        )
