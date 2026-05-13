from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.audio import AudioData, AudioDataStamped


class ReassembleAudioAdapter(BaseAdapter[AudioDataStamped]):
    """
    Adapter for `audio` topic from Reassemble datasets.

    Translated from `audio` message (custom Protocol Buffers) to
    `AudioDataStamped`.
    """

    adapter_id = "reassemble.audio"
    _REQUIRED_KEYS: tuple[str, ...] = ("ts_start", "audio")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `audio` payload into a `AudioDataStamped` message.

        Args:
            payload: Raw payload from the `audio` topic.

        Returns:
            A `Message` containing the `AudioDataStamped` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["ts_start"] * 1e9),
            data=AudioDataStamped(
                audio_data=AudioData(data=bytes(payload["audio"])),
            ),
        )
