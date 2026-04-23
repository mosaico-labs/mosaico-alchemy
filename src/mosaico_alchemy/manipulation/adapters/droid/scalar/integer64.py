from mosaicolabs import Integer64, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidInteger64Adapter(BaseAdapter):
    adapter_id = "droid.integer64"
    ontology_type = Integer64

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Integer64(data=int(payload.get("value", 0))),
        )
