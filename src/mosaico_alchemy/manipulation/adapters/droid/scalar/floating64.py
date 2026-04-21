from mosaicolabs import Floating64, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class DroidFloating64Adapter(BaseAdapter):
    adapter_id = "droid.floating64"
    ontology_type = Floating64

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Floating64(data=float(payload.get("value", 0.0))),
        )
