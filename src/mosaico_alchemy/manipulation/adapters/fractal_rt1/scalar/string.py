from mosaicolabs import Message, String

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1StringAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.string"
    ontology_type = String

    @classmethod
    def translate(cls, payload: dict) -> Message:
        value = payload.get("value")

        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")

        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=String(data=str(value)),
        )
