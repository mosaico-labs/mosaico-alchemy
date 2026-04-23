from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.terminate_episode import (
    TerminateEpisode,
)


class FractalRT1TerminateEpisodeAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.terminate_episode"
    ontology_type = TerminateEpisode

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=TerminateEpisode(
                terminate_episode=[int(value) for value in payload.get("value", [])]
            ),
        )
