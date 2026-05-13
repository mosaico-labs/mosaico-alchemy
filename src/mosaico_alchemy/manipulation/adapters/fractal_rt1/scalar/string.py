from mosaicolabs import Message, String

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1StringAdapter(BaseAdapter[String]):
    """
    Adapter for `string` topic from FractalRT1 datasets.

    Translated from `string` message (custom Protocol Buffers) to
    `mosaicolabs.String`.
    """

    adapter_id = "fractal_rt1.string"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `string` payload into a `mosaicolabs.String` message.

        Args:
            payload: Raw payload from the `string` topic.

        Returns:
            A `Message` containing the `mosaicolabs.String` data.
        """
        cls._validate_payload(payload=payload)
        value = payload["value"]
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=String(data=str(value)),
        )
