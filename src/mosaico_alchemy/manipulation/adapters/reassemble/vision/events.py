from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.event_camera import Event, EventCamera


class ReassembleEventsAdapter(BaseAdapter[EventCamera]):
    """
    Adapter for `events` data in Reassemble datasets.

    Translates `events` data from the dataset's message format to the
    `EventCamera` ontology type.
    """

    adapter_id = "reassemble.events"
    _REQUIRED_KEYS: tuple[str, ...] = (
        "t_start_ns",
        "t_end_ns",
        "timestamp_ns",
        "events",
        "event_timestamps_ns",
    )

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `events` payload into a `EventCamera` message.

        Args:
            payload: Raw payload from the `events` topic.

        Returns:
            A `Message` containing the `EventCamera` data.
        """
        cls._validate_payload(
            payload=payload,
            constraints={
                "events": {"not_empty": True},
                "event_timestamps_ns": {"not_empty": True},
            },
        )
        t_start_ns = int(payload["t_start_ns"])

        events = [
            Event(
                x=int(event[0]),
                y=int(event[1]),
                polarity=int(event[2]),
                dt_ns=int(event_timestamp_ns) - t_start_ns,
            )
            for event, event_timestamp_ns in zip(
                payload["events"],
                payload["event_timestamps_ns"],
            )
        ]
        if not events:
            raise ValueError(
                "Unable to compose the list of `Event` objects from payload "
            )

        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=EventCamera(
                width=346,
                height=260,
                events=events,
                t_start_ns=t_start_ns,
                t_end_ns=int(payload["t_end_ns"]),
            ),
        )
