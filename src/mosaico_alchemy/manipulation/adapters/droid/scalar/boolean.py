from mosaicolabs import Boolean, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidBooleanAdapter(BaseAdapter[Boolean]):
    """
    Adapter for `boolean` topic from DROID datasets.

    Translated from `boolean` message (custom Protocol Buffers) to
    `mosaicolabs.Boolean`.
    """

    adapter_id = "droid.boolean"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "value")

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
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Boolean(data=bool(payload["value"])),
        )
