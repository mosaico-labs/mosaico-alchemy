from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase, register_default_adapter
from mosaicolabs.ros_bridge.adapters.helpers import _validate_msgdata

from mosaico_alchemy.manipulation.ontology import AudioData


@register_default_adapter
class AudioDataAdapter(ROSAdapterBase[AudioData]):
    """
    Adapter override for 'audio_common_msgs/msg/AudioData' to `AudioData` model.

    This adapter is used to convert ROS audio data to Mosaico AudioData.
    """

    ros_msgtype = "audio_common_msgs/msg/AudioData"
    __mosaico_ontology_type__ = AudioData
    _REQUIRED_KEYS = ("data",)

    @classmethod
    def from_dict(cls, ros_data: dict) -> AudioData:
        """Converts ROS audio data to Mosaico AudioData.

        Args:
            ros_data: ROS audio data.

        Returns:
            Mosaico AudioData.
        """
        _validate_msgdata(cls, ros_data)
        return AudioData(data=bytes(ros_data["data"]))

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
