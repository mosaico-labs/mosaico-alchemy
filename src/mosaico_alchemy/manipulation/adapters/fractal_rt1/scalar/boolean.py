from mosaicolabs import Boolean, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class FractalRT1BooleanAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.boolean"
    ontology_type = Boolean

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=Boolean(data=bool(payload.get("value"))),
        )
