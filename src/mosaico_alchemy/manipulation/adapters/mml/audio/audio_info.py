from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase, register_default_adapter
from mosaicolabs.ros_bridge.adapters.helpers import _validate_msgdata

from mosaico_alchemy.manipulation.ontology import AudioInfo
from mosaico_alchemy.manipulation.ontology.audio import AudioFormat


@register_default_adapter
class AudioInfoAdapter(ROSAdapterBase[AudioInfo]):
    """
    Default Adapter for 'audio_common_msgs/msg/AudioInfo' to `AudioInfo` model.
    """

    ros_msgtype = "audio_common_msgs/msg/AudioInfo"
    __mosaico_ontology_type__ = AudioInfo
    _REQUIRED_KEYS = (
        "channels",
        "sample_rate",
        "sample_format",
        "bitrate",
        "coding_format",
    )

    @classmethod
    def from_dict(cls, ros_data: dict) -> AudioInfo:
        """
        Converts ROS audio info to Mosaico AudioInfo.
        """
        _validate_msgdata(cls, ros_data)
        return AudioInfo(
            channels=int(ros_data["channels"]),
            sample_rate=int(ros_data["sample_rate"]),
            sample_format=str(ros_data["sample_format"]),
            bitrate=(None if ros_data["bitrate"] is None else int(ros_data["bitrate"])),
            coding_format=AudioFormat(str(ros_data["coding_format"])).lower(),
        )

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
