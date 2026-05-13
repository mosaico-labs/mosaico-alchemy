from mosaicolabs import Boolean, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1BooleanAdapter(BaseAdapter[Boolean]):
    """
    Adapter for `boolean` topic from FractalRT1 datasets.

    Translated from `boolean` message (custom Protocol Buffers) to
    `mosaicolabs.Boolean`.
    """

    adapter_id = "fractal_rt1.boolean"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `boolean` payload into a `mosaicolabs.Boolean` message.

        Args:
            payload: Raw payload from the `boolean` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Boolean` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Boolean(data=bool(payload["value"])),
        )
