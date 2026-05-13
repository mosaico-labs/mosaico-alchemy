from mosaicolabs import Message, Quaternion

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1QuaternionAdapter(BaseAdapter[Quaternion]):
    """
    Adapter for quaternion data in FractalRT1 datasets.

    Translates quaternion data from the dataset's message format to the
    `mosaicolabs.Quaternion` ontology type.
    """

    adapter_id = "fractal_rt1.quaternion"
    ontology_type = Quaternion
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "vector")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `quaternion` payload into a `Quaternion` message.

        Args:
            payload: Raw payload from the `quaternion` topic.

        Returns:
            A `Message` containing the `Quaternion` data.
        """
        cls._validate_payload(payload=payload, constraints={"vector": {"len": 4}})
        vector = payload["vector"]

        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Quaternion(
                w=vector[0],
                x=vector[1],
                y=vector[2],
                z=vector[3],
            ),
        )
