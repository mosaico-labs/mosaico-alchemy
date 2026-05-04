"""Adapter that translates Reassemble segment-boundary payloads into the
SegmentInfo ontology."""

from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.segment_info import SegmentInfo


class ReassembleSegmentInfoAdapter(BaseAdapter):
    adapter_id = "reassemble.segment_info"
    ontology_type = "segment_info"

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=SegmentInfo(
                action=payload.get("action", "grasp"),
                parent_action=payload.get("parent_action"),
                success=bool(payload.get("success", True)),
                is_terminal=bool(payload.get("is_terminal", False)),
            ),
        )
