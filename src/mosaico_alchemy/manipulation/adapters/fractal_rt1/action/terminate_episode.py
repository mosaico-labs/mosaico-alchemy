from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.terminate_episode import (
    TerminateEpisode,
)


class FractalRT1TerminateEpisodeAdapter(BaseAdapter[TerminateEpisode]):
    """
    Adapter for `terminate_episode` topic from FractalRT1 datasets.

    Translated from `terminate_episode` message (custom Protocol Buffers) to
    `TerminateEpisode`.
    """

    adapter_id = "fractal_rt1.terminate_episode"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "value")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `terminate_episode` payload into a `TerminateEpisode` message.

        Args:
            payload: Raw payload from the `terminate_episode` topic.

        Returns:
            A `Message` containing the `TerminateEpisode` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=TerminateEpisode(
                terminate_episode=[int(value) for value in payload["value"]]
            ),
        )
