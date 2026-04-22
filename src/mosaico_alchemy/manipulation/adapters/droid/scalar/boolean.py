from mosaicolabs import Boolean, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class DroidBooleanAdapter(BaseAdapter):
    adapter_id = "droid.boolean"
    ontology_type = Boolean

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Boolean(data=bool(payload.get("value", False))),
        )
