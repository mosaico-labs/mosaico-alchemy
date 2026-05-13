from mosaicolabs import Integer64, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidInteger64Adapter(BaseAdapter[Integer64]):
    """
    Adapter for `integer64` topic from DROID datasets.

    Translated from `integer64` message (custom Protocol Buffers) to
    `mosaicolabs.Integer64`.
    """

    adapter_id = "droid.integer64"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `integer64` payload into a `mosaicolabs.Integer64` message.

        Args:
            payload: Raw payload from the `integer64` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Integer64` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Integer64(data=int(payload["value"])),
        )
