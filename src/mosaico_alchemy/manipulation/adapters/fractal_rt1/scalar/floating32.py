from mosaicolabs import Floating32, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1Floating32Adapter(BaseAdapter[Floating32]):
    """
    Adapter for `floating32` topic from FractalRT1 datasets.

    Translated from `floating32` message (custom Protocol Buffers) to
    `mosaicolabs.Floating32`.
    """

    adapter_id = "fractal_rt1.floating32"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `floating32` payload into a `mosaicolabs.Floating32` message.

        Args:
            payload: Raw payload from the `floating32` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Floating32` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Floating32(data=float(payload["value"])),
        )
