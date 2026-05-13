"""Adapter that translates Reassemble segment-boundary payloads into the
SegmentInfo ontology."""

from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.segment_info import SegmentInfo


class ReassembleSegmentInfoAdapter(BaseAdapter[SegmentInfo]):
    """
    Adapter for `segment_info` data in Reassemble datasets.

    Translates `segment_info` data from the dataset's message format to the
    `SegmentInfo` ontology type.
    """

    adapter_id = "reassemble.segment_info"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp",)

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `segment_info` payload into a `SegmentInfo` message.

        Args:
            payload: Raw payload from the `segment_info` topic.

        Returns:
            A `Message` containing the `SegmentInfo` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=SegmentInfo(
                action=payload.get("action", "grasp"),
                parent_action=payload.get("parent_action"),
                success=bool(payload.get("success", True)),
                is_terminal=bool(payload.get("is_terminal", False)),
            ),
        )
