from mosaicolabs import Floating32, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class FractalRT1Floating32Adapter(BaseAdapter):
    adapter_id = "fractal_rt1.floating32"
    ontology_type = Floating32

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=Floating32(data=float(payload.get("value", 0.0))),
        )
