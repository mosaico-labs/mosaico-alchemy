from mosaicolabs import Message, Vector3d, Velocity

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidVelocityAdapter(BaseAdapter[Velocity]):
    """
    Adapter for `velocity` data in DROID datasets.

    Translates `velocity` data from the dataset's message format to the
    `mosaicolabs.Velocity` ontology type.
    """

    adapter_id = "droid.velocity"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "velocity")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `velocity` payload into a `mosaicolabs.Velocity` message.

        Args:
            payload: Raw payload from the `velocity` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Velocity` data.
        """
        cls._validate_payload(payload=payload, constraints={"velocity": {"len": 6}})
        velocity = payload["velocity"]

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Velocity(
                linear=Vector3d.from_list(velocity[:3]),
                angular=Vector3d.from_list(velocity[3:]),
            ),
        )
