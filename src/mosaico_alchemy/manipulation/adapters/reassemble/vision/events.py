from mosaicolabs import Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter
from mosaicopacks.manipulation.ontology.event_camera import Event, EventCamera


class ReassembleEventsAdapter(BaseAdapter):
    adapter_id = "reassemble.events"
    ontology_type = EventCamera

    @classmethod
    def translate(cls, payload: dict) -> Message:
        t_start_ns = int(payload.get("t_start_ns", 0.0))

        events = [
            Event(
                x=int(event[0]),
                y=int(event[1]),
                polarity=int(event[2]),
                dt_ns=int(event_timestamp_ns) - t_start_ns,
            )
            for event, event_timestamp_ns in zip(
                payload.get("events", []),
                payload.get("event_timestamps_ns", []),
            )
        ]

        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=EventCamera(
                width=346,
                height=260,
                events=events,
                t_start_ns=t_start_ns,
                t_end_ns=int(payload.get("t_end_ns", 0.0)),
            ),
        )
