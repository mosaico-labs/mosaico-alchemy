from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.audio import AudioData, AudioDataStamped


class ReassembleAudioAdapter(BaseAdapter):
    adapter_id = "reassemble.audio"
    ontology_type = AudioDataStamped

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("ts_start", 0.0) * 1e9),
            data=AudioDataStamped(
                audio_data=AudioData(
                    data=bytes(payload.get("audio")),
                ),
            ),
        )
