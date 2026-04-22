from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase

from mosaicopacks.manipulation.ontology import AudioData


class AudioDataAdapter(ROSAdapterBase[AudioData]):
    ros_msgtype = "audio_common_msgs/msg/AudioData"
    __mosaico_ontology_type__ = AudioData
    _REQUIRED_KEYS = ("data",)

    @classmethod
    def from_dict(cls, ros_data: dict) -> AudioData:
        return AudioData(data=bytes(ros_data.get("data")))

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
