from mosaicolabs import Floating64, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidFloating64Adapter(BaseAdapter[Floating64]):
    """
    Adapter for `floating64` topic from DROID datasets.

    Translated from `floating64` message (custom Protocol Buffers) to
    `mosaicolabs.Floating64`.
    """

    adapter_id = "droid.floating64"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `floating64` payload into a `mosaicolabs.Floating64` message.

        Args:
            payload: Raw payload from the `floating64` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Floating64` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Floating64(data=float(payload["value"])),
        )
